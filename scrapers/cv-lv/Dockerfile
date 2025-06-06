FROM daviskylv/work-scraper-utils:latest

# Set working directory
WORKDIR /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Start scraping
CMD ["python", "scraper.py"]