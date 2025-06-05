FROM daviskylv/work-scraper-utils:latest

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set working directory
WORKDIR /app
COPY . /app

# Start scraping
CMD ["python", "scraper.py"]