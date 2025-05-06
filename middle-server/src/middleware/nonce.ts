import { Request, Response, NextFunction } from 'express';
import crypto from 'crypto';

// Store of used nonces to prevent replay attacks
const usedNonces = new Set<string>();

// Max age for nonces (5 minutes)
const NONCE_MAX_AGE_MS = 5 * 60 * 1000;

// Nonce generation and validation interface
export interface NonceMiddleware {
  generateNonce(): string;
  validateNonce(nonce: string, timestamp: number): boolean;
}

export class DefaultNonceMiddleware implements NonceMiddleware {
  /**
   * Generate a cryptographically secure random nonce
   * @returns {string} Base64 encoded nonce
   */
  generateNonce(): string {
    return crypto.randomBytes(32).toString('base64');
  }

  /**
   * Validate a nonce to prevent replay attacks
   * @param nonce - The nonce to validate
   * @param timestamp - Timestamp of the request
   * @returns {boolean} Whether the nonce is valid
   */
  validateNonce(nonce: string, timestamp: number): boolean {
    // Check if nonce has been used before
    if (usedNonces.has(nonce)) {
      return false;
    }

    // Check timestamp is not too old
    const currentTime = Date.now();
    if (Math.abs(currentTime - timestamp) > NONCE_MAX_AGE_MS) {
      return false;
    }

    // Mark nonce as used and clean up old nonces
    usedNonces.add(nonce);
    this.cleanupNonces();

    return true;
  }

  /**
   * Clean up old nonces from the set
   * @private
   */
  private cleanupNonces(): void {
    const currentTime = Date.now();
    for (const nonce of usedNonces) {
      // Remove nonces that are too old
      if (Math.abs(currentTime - parseInt(nonce.split('_')[1])) > NONCE_MAX_AGE_MS) {
        usedNonces.delete(nonce);
      }
    }
  }
}

/**
 * Middleware to validate request nonce
 * @param nonceMiddleware - Nonce middleware implementation
 * @returns {Function} Express middleware function
 */
export const createNonceMiddleware = (
  nonceMiddleware: NonceMiddleware = new DefaultNonceMiddleware()
) => {
  return (req: Request, res: Response, next: NextFunction) => {
    const { nonce, timestamp } = req.headers;

    // Nonce and timestamp are required
    if (!nonce || !timestamp) {
      return res.status(400).json({ 
        error: 'Nonce and timestamp are required' 
      });
    }

    // Validate nonce
    const isValid = nonceMiddleware.validateNonce(
      nonce as string, 
      parseInt(timestamp as string, 10)
    );

    if (!isValid) {
      return res.status(401).json({ 
        error: 'Invalid or expired nonce' 
      });
    }

    next();
  };
};

export default createNonceMiddleware();