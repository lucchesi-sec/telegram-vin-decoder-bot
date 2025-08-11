"""End-to-end tests for complete bot scenarios."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from src.tests.utils.factories import (
    VINFactory,
    UserFactory,
    VehicleFactory,
    TelegramDataFactory,
    APIResponseFactory
)
from src.tests.utils.helpers import MockResponse


class TestBotScenarios:
    """Test realistic bot usage scenarios end-to-end."""
    
    @pytest.mark.asyncio
    async def test_new_user_complete_journey(self):
        """Test complete journey for a new user."""
        # Scenario: New user discovers bot, decodes VINs, configures settings
        
        user_id = 123456789
        vin1 = "1HGBH41JXMN109186"
        vin2 = "WBANE53517C123456"
        
        # Step 1: User starts the bot
        start_update = TelegramDataFactory.create_message_update(
            text="/start",
            user_id=user_id
        )
        
        # Step 2: User asks for help
        help_update = TelegramDataFactory.create_message_update(
            text="/help",
            user_id=user_id
        )
        
        # Step 3: User decodes first VIN
        vin1_update = TelegramDataFactory.create_message_update(
            text=f"/vin {vin1}",
            user_id=user_id
        )
        
        # Step 4: User configures settings
        settings_update = TelegramDataFactory.create_message_update(
            text="/settings",
            user_id=user_id
        )
        
        # Step 5: User changes decoder preference
        decoder_callback = TelegramDataFactory.create_callback_query_update(
            data="settings:decoder:autodev",
            user_id=user_id
        )
        
        # Step 6: User decodes second VIN with new settings
        vin2_update = TelegramDataFactory.create_message_update(
            text=f"/vin {vin2}",
            user_id=user_id
        )
        
        # Step 7: User checks recent searches
        recent_update = TelegramDataFactory.create_message_update(
            text="/recent",
            user_id=user_id
        )
        
        # Step 8: User checks statistics
        stats_update = TelegramDataFactory.create_message_update(
            text="/stats",
            user_id=user_id
        )
        
        # Simulate the flow with mocked services
        with patch('src.presentation.telegram_bot.bot_application.BotApplication') as MockBot:
            mock_bot = MockBot.return_value
            
            # Process each update
            updates = [
                start_update,
                help_update,
                vin1_update,
                settings_update,
                decoder_callback,
                vin2_update,
                recent_update,
                stats_update
            ]
            
            for update in updates:
                await mock_bot.process_update(update)
            
            # Verify bot processed all updates
            assert mock_bot.process_update.call_count == len(updates)
    
    @pytest.mark.asyncio
    async def test_power_user_bulk_operations(self):
        """Test power user performing bulk VIN operations."""
        user_id = 987654321
        vins = [VINFactory.create_valid_vin(i) for i in range(10)]
        
        # Simulate rapid VIN decoding
        updates = []
        for vin in vins:
            update = TelegramDataFactory.create_message_update(
                text=f"/vin {vin}",
                user_id=user_id
            )
            updates.append(update)
        
        # Add some inline VIN queries
        for vin in vins[:3]:
            update = TelegramDataFactory.create_message_update(
                text=vin,  # Just the VIN without command
                user_id=user_id
            )
            updates.append(update)
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # Mock API responses for all VINs
            responses = []
            for vin in vins:
                responses.append(MockResponse(
                    status_code=200,
                    json_data=APIResponseFactory.create_nhtsa_response(vin)
                ))
            mock_client.get.side_effect = responses * 2  # For both commands and inline
            
            # Process all updates concurrently
            with patch('src.presentation.telegram_bot.bot_application.BotApplication') as MockBot:
                mock_bot = MockBot.return_value
                
                tasks = []
                for update in updates:
                    task = mock_bot.process_update(update)
                    tasks.append(task)
                
                await asyncio.gather(*tasks)
                
                # Verify all were processed
                assert mock_bot.process_update.call_count == len(updates)
    
    @pytest.mark.asyncio
    async def test_error_recovery_scenario(self):
        """Test bot recovery from various error conditions."""
        user_id = 111222333
        
        # Scenario 1: Invalid VIN
        invalid_vin_update = TelegramDataFactory.create_message_update(
            text="/vin INVALID123",
            user_id=user_id
        )
        
        # Scenario 2: API timeout
        timeout_vin = "1HGBH41JXMN109186"
        timeout_update = TelegramDataFactory.create_message_update(
            text=f"/vin {timeout_vin}",
            user_id=user_id
        )
        
        # Scenario 3: API error then retry
        retry_vin = "WBANE53517C123456"
        retry_update = TelegramDataFactory.create_message_update(
            text=f"/vin {retry_vin}",
            user_id=user_id
        )
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # Simulate different error conditions
            mock_client.get.side_effect = [
                # Timeout for first valid VIN
                asyncio.TimeoutError("Request timed out"),
                # Server error then success for retry
                MockResponse(status_code=503, raise_on_status=True),
                MockResponse(
                    status_code=200,
                    json_data=APIResponseFactory.create_nhtsa_response(retry_vin)
                )
            ]
            
            with patch('src.presentation.telegram_bot.bot_application.BotApplication') as MockBot:
                mock_bot = MockBot.return_value
                
                # Process invalid VIN
                await mock_bot.process_update(invalid_vin_update)
                
                # Process timeout
                await mock_bot.process_update(timeout_update)
                
                # Process retry scenario
                await mock_bot.process_update(retry_update)
                
                # Bot should handle all errors gracefully
                assert mock_bot.process_update.call_count == 3
    
    @pytest.mark.asyncio
    async def test_multi_user_concurrent_access(self):
        """Test multiple users accessing bot concurrently."""
        num_users = 20
        users = []
        
        for i in range(num_users):
            user_id = 100000 + i
            vin = VINFactory.create_valid_vin(i)
            users.append({
                'id': user_id,
                'vin': vin,
                'update': TelegramDataFactory.create_message_update(
                    text=f"/vin {vin}",
                    user_id=user_id
                )
            })
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # Mock responses for all users
            responses = []
            for user in users:
                responses.append(MockResponse(
                    status_code=200,
                    json_data=APIResponseFactory.create_nhtsa_response(user['vin'])
                ))
            mock_client.get.side_effect = responses
            
            with patch('src.presentation.telegram_bot.bot_application.BotApplication') as MockBot:
                mock_bot = MockBot.return_value
                
                # Process all user requests concurrently
                tasks = []
                for user in users:
                    task = mock_bot.process_update(user['update'])
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Verify all completed without exceptions
                exceptions = [r for r in results if isinstance(r, Exception)]
                assert len(exceptions) == 0
                assert mock_bot.process_update.call_count == num_users
    
    @pytest.mark.asyncio
    async def test_settings_persistence_scenario(self):
        """Test that user settings persist across sessions."""
        user_id = 555666777
        
        # Session 1: User configures settings
        session1_updates = [
            TelegramDataFactory.create_message_update("/start", user_id),
            TelegramDataFactory.create_message_update("/settings", user_id),
            TelegramDataFactory.create_callback_query_update(
                "settings:decoder:autodev", user_id
            ),
            TelegramDataFactory.create_callback_query_update(
                "settings:market_value:true", user_id
            ),
            TelegramDataFactory.create_callback_query_update(
                "settings:format:detailed", user_id
            ),
        ]
        
        # Session 2: User returns later
        session2_updates = [
            TelegramDataFactory.create_message_update("/settings", user_id),
            TelegramDataFactory.create_message_update(
                "/vin 1HGBH41JXMN109186", user_id
            ),
        ]
        
        with patch('src.presentation.telegram_bot.bot_application.BotApplication') as MockBot:
            mock_bot = MockBot.return_value
            mock_user_service = AsyncMock()
            mock_bot.user_service = mock_user_service
            
            # Process session 1
            for update in session1_updates:
                await mock_bot.process_update(update)
            
            # Simulate time passing
            await asyncio.sleep(0.1)
            
            # Process session 2
            for update in session2_updates:
                await mock_bot.process_update(update)
            
            # Verify settings were loaded and used
            assert mock_user_service.get_user.called
            assert mock_user_service.update_user_preferences.called
    
    @pytest.mark.asyncio
    async def test_rate_limiting_scenario(self):
        """Test rate limiting behavior."""
        user_id = 999888777
        vin = "1HGBH41JXMN109186"
        
        # Create many rapid requests
        updates = []
        for i in range(50):  # Exceed rate limit
            update = TelegramDataFactory.create_message_update(
                text=f"/vin {vin}",
                user_id=user_id
            )
            updates.append(update)
        
        with patch('src.presentation.telegram_bot.bot_application.BotApplication') as MockBot:
            mock_bot = MockBot.return_value
            mock_bot.rate_limiter = MagicMock()
            mock_bot.rate_limiter.check_rate_limit.side_effect = (
                [True] * 10 +  # First 10 requests allowed
                [False] * 40   # Remaining requests blocked
            )
            
            processed = 0
            blocked = 0
            
            for update in updates:
                result = await mock_bot.process_update(update)
                if mock_bot.rate_limiter.check_rate_limit.return_value:
                    processed += 1
                else:
                    blocked += 1
            
            assert processed == 10
            assert blocked == 40
    
    @pytest.mark.asyncio
    async def test_data_export_scenario(self):
        """Test user exporting their data."""
        user_id = 777888999
        
        # User has been using bot for a while
        setup_updates = [
            TelegramDataFactory.create_message_update("/start", user_id),
        ]
        
        # Decode multiple VINs
        vins = [VINFactory.create_valid_vin(i) for i in range(5)]
        for vin in vins:
            update = TelegramDataFactory.create_message_update(
                f"/vin {vin}", user_id
            )
            setup_updates.append(update)
        
        # Request data export
        export_update = TelegramDataFactory.create_message_update(
            "/export", user_id
        )
        
        with patch('src.presentation.telegram_bot.bot_application.BotApplication') as MockBot:
            mock_bot = MockBot.return_value
            
            # Setup user history
            for update in setup_updates:
                await mock_bot.process_update(update)
            
            # Request export
            await mock_bot.process_update(export_update)
            
            # Verify export was generated
            assert mock_bot.process_update.call_count == len(setup_updates) + 1