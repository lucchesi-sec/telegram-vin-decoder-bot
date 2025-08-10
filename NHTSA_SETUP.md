# NHTSA VIN Decoder Setup

The bot now uses the free NHTSA (National Highway Traffic Safety Administration) VIN decoder by default.

## Key Changes

1. **No API Key Required**: NHTSA is a free government service that doesn't require an API key
2. **Simplified Configuration**: Only the Telegram bot token is now required
3. **Removed Settings Menu**: The bot no longer has a `/settings` command since there's only one decoder
4. **Cleaner Code**: Removed complexity around service selection and API key management

## Configuration

You only need to set one environment variable:

```bash
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
```

The `CARSXE_API_KEY` is no longer required.

## Features

NHTSA provides the following vehicle information:
- Make and Model
- Year
- Body Type
- Manufacturer
- Vehicle Type
- Plant Location (City, State, Country)
- Engine Specifications (when available)
- Fuel Type
- Drive Type
- Transmission Type

## Testing

To test NHTSA VIN decoding:

```python
from vinbot.nhtsa_client import NHTSAClient

client = NHTSAClient()
result = await client.decode_vin("5UXWX7C57E0D12632")
print(result)
```

## Sample VINs for Testing

- `1HGBH41JXMN109186` - 1991 Honda
- `WBAPM7G50ANL92340` - 2010 BMW 335i
- `5UXWX7C57E0D12632` - 2014 BMW X3

## Limitations

- NHTSA provides basic vehicle information (no market value or history data)
- Best coverage for US vehicles
- Some fields may not be available for all vehicles
- Response times may vary based on NHTSA server load