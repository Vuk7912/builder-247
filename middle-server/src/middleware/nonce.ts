import { Request, Response, NextFunction } from 'express';
import crypto from 'crypto';
import { logger } from '../utils/logging'; // Assuming a centralized logging utility

// Nonce configuration
const NONCE_MAX_AGE_MS = 5 * 60 * 1000; // 5 minutes
const MAX_NONCE_STORAGE = 10000; // Limit nonce storage to prevent memory issues

class NonceManager {
  private usedNonces: Map<string, number>;

  constructor() {
    this.usedNonces = new Map();
  }

  /**
   * Generate a secure nonce
   * @returns {string} Base64 encoded nonce
   */
  generateNonce(): string {
    return crypto.randomBytes(32).toString('base64');
  }

  /**
   * Validate and track nonce
   * @param nonce - Nonce to validate
   * @param timestamp - Request timestamp
   * @returns {boolean} Nonce validity
   */
  validateNonce(nonce: string, timestamp: number): boolean {
    const currentTime = Date.now();

    // Check timestamp is within acceptable range
    if (Math.abs(currentTime - timestamp) > NONCE_MAX_AGE_MS) {
      logger.warn(`Nonce validation failed: Timestamp out of range`, { 
        currentTime, 
        timestamp 
      });
      return false;
    }

    // Check if nonce has been used
    if (this.usedNonces.has(nonce)) {
      logger.warn(`Nonce validation failed: Nonce already used`, { nonce });
      return false;
    }

    // Track the nonce
    this.usedNonces.set(nonce, currentTime);

    // Periodic cleanup to prevent memory growth
    this.cleanupNonces(currentTime);

    return true;
  }

  /**
   * Clean up old nonces to prevent memory growth
   * @param currentTime - Current timestamp
   */
  private cleanupNonces(currentTime: number): void {
    // Prevent unbounded growth
    if (this.usedNonces.size > MAX_NONCE_STORAGE) {
      const oldestEntries = Array.from(this.usedNonces.entries())
        .sort((a, b) => a[1] - b[1])
        .slice(0, this.usedNonces.size - MAX_NONCE_STORAGE);

      oldestEntries.forEach(([nonce]) => {
        this.usedNonces.delete(nonce);
      });
    }

    // Remove nonces older than max age
    for (const [nonce, timestamp] of this.usedNonces.entries()) {
      if (currentTime - timestamp > NONCE_MAX_AGE_MS) {
        this.usedNonces.delete(nonce);
      }
    }
  }
}

// Singleton instance of NonceManager
const nonceManager = new NonceManager();

/**
 * Nonce middleware for request authentication
 * @param req - Express request
 * @param res - Express response
 * @param next - Next middleware function
 */
export function nonceMiddleware(req: Request, res: Response, next: NextFunction): void {
  const { nonce, timestamp } = req.headers;

  // Validate presence of nonce and timestamp
  if (!nonce || !timestamp) {
    logger.warn('Nonce or timestamp missing', { 
      nonce: !!nonce, 
      timestamp: !!timestamp 
    });
    res.status(400).json({ 
      error: 'Nonce and timestamp are required' 
    });
    return;
  }

  // Parse timestamp
  const timestampNum = parseInt(timestamp as string, 10);
  if (isNaN(timestampNum)) {
    logger.warn('Invalid timestamp format', { timestamp });
    res.status(400).json({ 
      error: 'Invalid timestamp format' 
    });
    return;
  }

  // Validate nonce
  const isValid = nonceManager.validateNonce(
    nonce as string, 
    timestampNum
  );

  if (!isValid) {
    logger.warn('Nonce validation failed', { 
      nonce, 
      timestamp: timestampNum 
    });
    res.status(400).json({ 
      error: 'Invalid or expired nonce' 
    });
    return;
  }

  next();
}

export function generateNonce(): string {
  return nonceManager.generateNonce();
}

export default nonceMiddleware;