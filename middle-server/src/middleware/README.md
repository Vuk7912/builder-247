# Nonce Middleware

## Purpose
The Nonce Middleware provides an additional layer of security to prevent replay attacks and ensure request authenticity.

## Features
- Generates cryptographically secure nonces
- Validates request timestamps
- Prevents replay attacks
- Configurable nonce lifetime

## How It Works
1. Each sensitive request must include two headers:
   - `nonce`: A unique, cryptographically secure random string
   - `timestamp`: The current timestamp in milliseconds

2. Validation Checks:
   - Nonce must be present and unique
   - Timestamp must be within a 5-minute window
   - Prevents reusing nonces

## Usage Example
```typescript
// Client-side request
const nonce = generateNonce();
const timestamp = Date.now();

fetch('/your/route', {
  method: 'POST',
  headers: {
    'nonce': nonce,
    'timestamp': timestamp.toString()
  }
});
```

## Security Benefits
- Prevents replay attacks
- Adds request authentication layer
- Configurable and extensible

## Configuration
- Default nonce lifetime: 5 minutes
- Maximum nonce storage: 10,000 entries