import winston from 'winston';

// Configure Winston logger
export const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.splat(),
    winston.format.json()
  ),
  defaultMeta: { service: 'middle-server' },
  transports: [
    // Console transport for development
    new winston.transports.Console({
      format: winston.format.simple()
    }),
    // File transport for security audit logs
    new winston.transports.File({ 
      filename: 'logs/security-audit.log',
      level: 'warn'
    })
  ]
});

// Ensure unhandled rejections and exceptions are logged
process.on('unhandledRejection', (reason, promise) => {
  logger.error('Unhandled Rejection at:', promise, 'reason:', reason);
});

process.on('uncaughtException', (error) => {
  logger.error('Uncaught Exception:', error);
  process.exit(1);
});

export default logger;