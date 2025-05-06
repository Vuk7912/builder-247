import { Request, Response, NextFunction } from 'express';
import { DefaultNonceMiddleware, createNonceMiddleware } from '../../src/middleware/nonce';

describe('Nonce Middleware', () => {
  describe('DefaultNonceMiddleware', () => {
    let nonceMiddleware: DefaultNonceMiddleware;

    beforeEach(() => {
      nonceMiddleware = new DefaultNonceMiddleware();
    });

    it('should generate a unique nonce', () => {
      const nonce1 = nonceMiddleware.generateNonce();
      const nonce2 = nonceMiddleware.generateNonce();
      expect(nonce1).not.toEqual(nonce2);
    });

    it('should validate a fresh nonce', () => {
      const nonce = nonceMiddleware.generateNonce();
      const timestamp = Date.now();
      const isValid = nonceMiddleware.validateNonce(nonce, timestamp);
      expect(isValid).toBeTruthy();
    });

    it('should reject a reused nonce', () => {
      const nonce = nonceMiddleware.generateNonce();
      const timestamp = Date.now();
      
      // First validation should succeed
      const firstValidation = nonceMiddleware.validateNonce(nonce, timestamp);
      expect(firstValidation).toBeTruthy();

      // Second validation should fail
      const secondValidation = nonceMiddleware.validateNonce(nonce, timestamp);
      expect(secondValidation).toBeFalsy();
    });

    it('should reject an old nonce', () => {
      const nonce = nonceMiddleware.generateNonce();
      const oldTimestamp = Date.now() - (6 * 60 * 1000); // 6 minutes ago
      
      const isValid = nonceMiddleware.validateNonce(nonce, oldTimestamp);
      expect(isValid).toBeFalsy();
    });
  });

  describe('createNonceMiddleware', () => {
    let mockReq: Partial<Request>;
    let mockRes: Partial<Response>;
    let mockNext: NextFunction;
    let nonceMiddleware: DefaultNonceMiddleware;

    beforeEach(() => {
      nonceMiddleware = new DefaultNonceMiddleware();
      
      mockRes = {
        status: jest.fn().mockReturnThis(),
        json: jest.fn()
      };
      mockNext = jest.fn();
    });

    it('should reject request without nonce', () => {
      mockReq = {
        headers: {}
      };

      const middleware = createNonceMiddleware(nonceMiddleware);
      middleware(mockReq as Request, mockRes as Response, mockNext);

      expect(mockRes.status).toHaveBeenCalledWith(400);
      expect(mockRes.json).toHaveBeenCalledWith(
        expect.objectContaining({ error: 'Nonce and timestamp are required' })
      );
    });

    it('should call next for valid nonce', () => {
      const nonce = nonceMiddleware.generateNonce();
      const timestamp = Date.now();

      mockReq = {
        headers: {
          nonce,
          timestamp: timestamp.toString()
        }
      };

      const middleware = createNonceMiddleware(nonceMiddleware);
      middleware(mockReq as Request, mockRes as Response, mockNext);

      expect(mockNext).toHaveBeenCalled();
    });

    it('should reject invalid nonce', () => {
      mockReq = {
        headers: {
          nonce: 'invalid-nonce',
          timestamp: Date.now().toString()
        }
      };

      const middleware = createNonceMiddleware(nonceMiddleware);
      middleware(mockReq as Request, mockRes as Response, mockNext);

      expect(mockRes.status).toHaveBeenCalledWith(401);
      expect(mockRes.json).toHaveBeenCalledWith(
        expect.objectContaining({ error: 'Invalid or expired nonce' })
      );
    });
  });
});