# E-shop backend 

##  1. Goal's of creating this project
***
### 1.1 Django, Django-Rest-Framework.
* Understands how to:
  - [x] Write api's.
  - [x] Send query requests to db using django orm.
  - [x] Optimize ORM-Query using `.prefetch_related()`, `.select_related()`.
  - [x] Write tests using django tests.

### 1.2 Docker + Docker Compose.
* Understands how to:
  - [x] Create and set-up Dockerfile.
  - [x] Load image from dockerhub(Postgresql) + set-up.
  - [x] Run docker-compose and run commands inside containers. 

### 1.3 Postman.
* Understands how to create:
  - [x] Collections.
  - [x] Requests.
  - [x] Example of responses
  - [x] Environment.

## 2. Steck
***
* Lang. - Python3.11
* Framework - Django(4.2.1) + Django-Rest-Framework(3.14.0)
* DB - PostgreSQL(14.1)
* Other Libraries:
  * django-rest-passwordreset(1.3.0)
  * djangorestframework-simplejwt(5.2.2)
  * django-filter(23.2)
* API Platform - Postman(9.31.28)

## 3. [DB-Schema](https://dbdiagram.io/d/65152138ffbf5169f0a6f384)
***
[![diagram](https://i.postimg.cc/YCKPM7xr/Screenshot-from-2023-10-07-14-00-15.png)](https://postimg.cc/YhRRzJVZ)


## 4. How to run project
***

## Copy and run:
```gitexclude
# Copy project
git clone https://github.com/RomanShyshcenko/drf_shop.git

# Add your .env set-up to .env_example and rename file to .env 

# Build docker-compose
docker-compose build

# Create and migrate migrations
docker-compose run --rm web sh -c "python manage.py makemigrations"
docker-compose run --rm web sh -c "python manage.py migrate"

# Run
docker-compose up
```
### You can test endpoints by going to the [localhost](http://localhost:8000/) or download Postman and import collection, you can find [collection](https://github.com/RomanShyshcenko/drf_shop/blob/main/DRF_shop.postman_collection.json) in project.

***
### Author: Shyshchenko Roman



