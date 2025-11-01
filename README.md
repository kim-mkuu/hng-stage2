# Country Project API

## Build a RESTful API that fetches country data from an external API

A RESTful API that fetches country data from external APIs, stores it in a MySQL database, and provides CRUD operations with exchange rate information.

## Features

- Fetch and cache country data from `restcountries.com`
- Retrieve exchange rates from `open.er-api.com`
- Calculate estimated GDP for each country
- Filter countries by region and currency
- Sort countries by GDP
- Generate summary images with top countries
- Full CRUD operations on country data

## Tech Stack

- **Framework**: Django 5.2.7 + Django REST Framework 3.16.1
- **Database**: MySQL (Railway)
- **Deployment**: Leapcell
- **Server**: Gunicorn
- **Image Processing**: Pillow

## Project Structure

```txt
hng-stage2/
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── countries/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── utils.py
│   └── urls.py
├── cache/
│   └── summary.png
├── manage.py
├── requirements.txt
└── .env
```

## Local Setup

### Prerequisites

- Python 3.10+
- MySQL 8.0+
- pip

### Installation Steps

1. **Clone the repository**

```bash
git clone https://github.com/kim-mkuu/hng-stage2.git
cd hng-stage2
```

2. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file in the root directory:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=country_api
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
```

5. **Create MySQL database**

```sql
CREATE DATABASE country_data CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ur_name'@'localhost' IDENTIFIED BY '****';
GRANT ALL PRIVILEGES ON country_data.* TO 'ur_name'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

6. **Run migrations**

```bash
python manage.py makemigrations
python manage.py migrate
```

7. **Run development server**

```bash
python manage.py runserver
```

The API will be available at:
-**Locally** `http://127.0.0.1:8000/countries/`
-**Remote** `https://hng-stage02.leapcell.app/countries/`

## API Endpoints

### 1. Refresh Countries Data

```bash
POST /countries/refresh/
```

Fetches country data and exchange rates, then caches in database.

**Response:**

```json
{
  "message": "Countries refreshed successfully",
  "total_countries": 250
}
```

### 2. Get All Countries

```bash
GET /countries/
```

Retrieves all countries with optional filters and sorting.

**Query Parameters:**

- `region` - Filter by region (e.g., `?region=Africa`)
- `currency` - Filter by currency code (e.g., `?currency=NGN`)
- `sort` - Sort by GDP (e.g., `?sort=gdp_desc` or `?sort=gdp_asc`)

**Example:**

```bash
GET /countries/?region=Africa&sort=gdp_desc
```

**Response:**

```json
[
  {
    "id": 1,
    "name": "Nigeria",
    "capital": "Abuja",
    "region": "Africa",
    "population": 206139589,
    "currency_code": "NGN",
    "exchange_rate": "1600.23",
    "estimated_gdp": "25767448125.20",
    "flag_url": "https://flagcdn.com/ng.svg",
    "last_refreshed_at": "2025-10-31T14:51:33Z"
  }
]
```

### 3. Get Country by Name

```bash
GET /countries/:name/
```

**Example:**

```bash
GET /countries/Nigeria/
```

### 4. Delete Country

```bash
DELETE /countries/:name/
```

**Response:**

```json
{
  "message": "Country 'Nigeria' deleted successfully"
}
```

### 5. Get Status

```bash
GET /status/
```

**Response:**

```json
{
  "total_countries": 250,
  "last_refreshed_at": "2025-10-31T14:51:33Z"
}
```

### 6. Get Summary Image

```bash
GET /countries/image/
```

Returns a PNG image with country statistics.

## Deployment on Leapcell with Railway MySQL

### Step 1: Setup Railway MySQL Database

1. Go to [Railway.app](https://railway.app/)
2. Create a new project
3. Add MySQL database service
4. Copy database credentials:
   - Host
   - Port
   - Database name
   - Username
   - Password

### Step 2: Prepare Project for Deployment

1. **Ensure requirements.txt includes production dependencies**

```txt
gunicorn==23.0.0
PyMySQL==1.1.2
```

2. **Update settings.py for production**

Database configuration already uses environment variables:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
    }
}
```

3. **Verify ALLOWED_HOSTS configuration**

```python
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')
```

### Step 3: Deploy to Leapcell

1. **Push code to GitHub**

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo>
git push -u origin main
```

2. **Create Leapcell account and new project**

   - Go to [Leapcell](https://leapcell.io/)
   - Create new project
   - Connect GitHub repository

3. **Configure Environment Variables in Leapcell**

Add the following variables:

```txt
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-app-domain.leapcell.dev,127.0.0.1,localhost

DB_NAME=railway
DB_USER=root
DB_PASSWORD=<railway-db-password>
DB_HOST=<railway-db-host>
DB_PORT=<railway-db-port>
```

4. **Set Build Command**

```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

5. **Set Start Command**

```bash
python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:8080 --timeout 300 --workers 2
```

6. **Deploy**
   - Click "Deploy" button
   - Wait for deployment to complete
   - Your API will be available at: `https://your-app-name.leapcell.dev`

### Step 4: Test Deployment

1. **Test refresh endpoint**

```bash
curl -X POST https://your-app-name.leapcell.dev/countries/refresh/
```

2. **Test status endpoint**

```bash
curl https://your-app-name.leapcell.dev/status/
```

3. **Test countries list**

```bash
curl https://your-app-name.leapcell.dev/countries/
```

## Environment Variables Reference

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| SECRET_KEY | Django secret key | Yes | `django-insecure-xxx` |
| DEBUG | Debug mode | Yes | `False` (production) |
| ALLOWED_HOSTS | Allowed host domains | Yes | `domain1.com,domain2.com` |
| DB_NAME | Database name | Yes | `railway` |
| DB_USER | Database user | Yes | `root` |
| DB_PASSWORD | Database password | Yes | `your_password` |
| DB_HOST | Database host | Yes | `caboose.proxy.rlwy.net` |
| DB_PORT | Database port | Yes | `42117` |

## Dependencies

See `requirements.txt` for full list. Key dependencies:

- Django==5.2.7
- djangorestframework==3.16.1
- gunicorn==23.0.0
- PyMySQL==1.1.2
- Pillow==12.0.0
- requests==2.32.5
- python-dotenv==1.2.1

## Error Handling

The API returns consistent JSON error responses:

- `400 Bad Request` - Validation errors
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server errors
- `503 Service Unavailable` - External API failures

**Example error response:**

```json
{
  "error": "Country not found"
}
```

## Data Refresh Behavior

- Matches countries by name (case-insensitive)
- Updates existing records or inserts new ones
- Recalculates estimated_gdp with fresh random multiplier (1000-2000)
- Handles multiple currencies by taking the first one
- Sets null values for missing exchange rates
- Updates global last_refreshed_at timestamp

## Troubleshooting

### Database Connection Issues

```bash
# Test MySQL connection from Railway
mysql -h <DB_HOST> -P <DB_PORT> -u <DB_USER> -p
```

### Migration Issues

```bash
# Reset migrations (development only)
python manage.py migrate countries zero
python manage.py migrate
```

### External API Timeout

- Default timeout is 10 seconds
- Check network connectivity
- Verify API endpoints are accessible

### Image Generation Issues

- Requires `/tmp` directory access on Leapcell for image persistence
- Font files must be available at `/usr/share/fonts/truetype/dejavu/`
- Falls back to default font if custom fonts unavailable

## License

MIT

## Author

kim-mkuu
