# Middleware Documentation

## Nonce Middleware

### Purpose
The Nonce Middleware provides an additional layer of security to prevent replay attacks and ensure request authenticity.

### How it Works
1. Each sensitive request must include two headers:
   - `nonce`: A unique, cryptographically secure random string
   - `timestamp`: The current timestamp in milliseconds

2. The middleware validates that:
   - The nonce has not been used before
   - The timestamp is within a valid time window (default: 5 minutes)

### Usage
```typescript
// Automatically applied to sensitive routes
router.post("/your/sensitive/route", handler);
```

### Client Example
```typescript
const nonce = generateNonce(); // Your nonce generation method
const timestamp = Date.now();

fetch('/your/route', {
  method: 'POST',
  headers: {
    'nonce': nonce,
    'timestamp': timestamp.toString()
  },
  // other request details
});
```

### Security Benefits
- Prevents replay attacks
- Ensures request freshness
- Adds a layer of request authentication

### Configurable Options
The nonce middleware can be customized by providing a custom `NonceMiddleware` implementation.