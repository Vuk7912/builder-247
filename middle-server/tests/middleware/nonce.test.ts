import { Request, Response, NextFunction } from 'express';
import { nonceMiddleware, generateNonce } from '../../src/middleware/nonce';
import { logger } from '../../src/utils/logging';

// Mock logger to prevent actual logging during tests
jest.mock('../../src/utils/logging', () => ({
  logger: {
    warn: jest.fn(),
    error: jest.fn()
  }
}));

describe('Nonce Middleware', () => {
  let mockReq: Partial<Request>;
  let mockRes: Partial<Response>;
  let mockNext: NextFunction;

  beforeEach(() => {
    mockReq = {
      headers: {}
    };

    mockRes = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };

    mockNext = jest.fn();

    // Clear mock calls before each test
    jest.clearAllMocks();
  });

  it('should generate unique nonces', () => {
    const nonce1 = generateNonce();
    const nonce2 = generateNonce();
    expect(nonce1).not.toEqual(nonce2);
  });

  it('should reject request without nonce', () => {
    mockReq.headers = { timestamp: Date.now().toString() };
    
    nonceMiddleware(mockReq as Request, mockRes as Response, mockNext);

    expect(mockRes.status).toHaveBeenCalledWith(400);
    expect(mockRes.json).toHaveBeenCalledWith(
      expect.objectContaining({ error: 'Nonce and timestamp are required' })
    );
    expect(mockNext).not.toHaveBeenCalled();
  });

  it('should reject request without timestamp', () => {
    mockReq.headers = { nonce: generateNonce() };
    
    nonceMiddleware(mockReq as Request, mockRes as Response, mockNext);

    expect(mockRes.status).toHaveBeenCalledWith(400);
    expect(mockRes.json).toHaveBeenCalledWith(
      expect.objectContaining({ error: 'Nonce and timestamp are required' })
    );
    expect(mockNext).not.toHaveBeenCalled();
  });

  it('should reject invalid timestamp format', () => {
    mockReq.headers = { 
      nonce: generateNonce(),
      timestamp: 'invalid-timestamp'
    };
    
    nonceMiddleware(mockReq as Request, mockRes as Response, mockNext);

    expect(mockRes.status).toHaveBeenCalledWith(400);
    expect(mockRes.json).toHaveBeenCalledWith(
      expect.objectContaining({ error: 'Invalid timestamp format' })
    );
    expect(mockNext).not.toHaveBeenCalled();
  });

  it('should reject nonce with old timestamp', () => {
    const oldTimestamp = Date.now() - (6 * 60 * 1000); // 6 minutes ago
    mockReq.headers = { 
      nonce: generateNonce(),
      timestamp: oldTimestamp.toString()
    };
    
    nonceMiddleware(mockReq as Request, mockRes as Response, mockNext);

    expect(mockRes.status).toHaveBeenCalledWith(400);
    expect(mockRes.json).toHaveBeenCalledWith(
      expect.objectContaining({ error: 'Invalid or expired nonce' })
    );
    expect(mockNext).not.toHaveBeenCalled();
  });

  it('should reject reused nonce', () => {
    const nonce = generateNonce();
    const currentTimestamp = Date.now();

    // First request should pass
    mockReq.headers = { 
      nonce: nonce,
      timestamp: currentTimestamp.toString()
    };
    
    nonceMiddleware(mockReq as Request, mockRes as Response, mockNext);
    expect(mockNext).toHaveBeenCalled();

    // Reset mocks for second request
    mockNext.mockClear();
    (mockRes.status as jest.Mock).mockClear();
    (mockRes.json as jest.Mock).mockClear();

    // Second request with same nonce should fail
    nonceMiddleware(mockReq as Request, mockRes as Response, mockNext);

    expect(mockRes.status).toHaveBeenCalledWith(400);
    expect(mockRes.json).toHaveBeenCalledWith(
      expect.objectContaining({ error: 'Invalid or expired nonce' })
    );
    expect(mockNext).not.toHaveBeenCalled();
  });

  it('should allow valid nonce', () => {
    mockReq.headers = { 
      nonce: generateNonce(),
      timestamp: Date.now().toString()
    };
    
    nonceMiddleware(mockReq as Request, mockRes as Response, mockNext);

    expect(mockNext).toHaveBeenCalled();
    expect(mockRes.status).not.toHaveBeenCalled();
  });
});