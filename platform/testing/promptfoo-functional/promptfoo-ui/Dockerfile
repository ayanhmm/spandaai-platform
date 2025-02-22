# Use an official Node.js runtime as the base image
FROM node:20-alpine as build

# Set working directory in the container
WORKDIR /usr/src/app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application files
COPY . .

# Build the application
RUN npm run build

# Use Nginx as the base image for serving the app
FROM nginx:stable-alpine

# Copy built React files from the build stage to Nginx's default html directory
COPY --from=build /usr/src/app/build /usr/share/nginx/html

# Copy a custom Nginx configuration file, if needed (optional)
# Uncomment the following line if you have a custom nginx.conf file
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]
