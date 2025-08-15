FROM n8nio/n8n:latest

# Set environment variables
ENV N8N_BASIC_AUTH_ACTIVE=false
ENV N8N_HOST=0.0.0.0
ENV N8N_PORT=5678
ENV N8N_PROTOCOL=https
ENV N8N_USER_MANAGEMENT_DISABLED=true
ENV N8N_DISABLE_PRODUCTION_MAIN_PROCESS=false

# Copy your workflow files
COPY n8n-workflows/ /home/node/.n8n/workflows/

# Expose port
EXPOSE 5678

# Start n8n
CMD ["n8n"]
