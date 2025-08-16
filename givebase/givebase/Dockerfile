# Frontend Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Install serve with proper configuration
RUN npm install -g serve

# Create a serve configuration file for better static handling
RUN echo '{\
  "public": "dist",\
  "rewrites": [\
    { "source": "/api/**", "destination": "http://backend:8000/api/**" },\
    { "source": "**", "destination": "/index.html" }\
  ],\
  "headers": [\
    {\
      "source": "**/*.(png|jpg|jpeg|gif|ico|svg|webp)",\
      "headers": [\
        { "key": "Cache-Control", "value": "public, max-age=31536000, immutable" },\
        { "key": "Content-Type", "value": "image/*" }\
      ]\
    },\
    {\
      "source": "**/*.webmanifest",\
      "headers": [\
        { "key": "Content-Type", "value": "application/manifest+json" }\
      ]\
    }\
  ]\
}' > serve.json

# Expose port
EXPOSE 3000

# Start the server with configuration
CMD ["serve", "-s", "dist", "-l", "3000", "-c", "serve.json"]