## Api-Endpoint
We built a small Flask API with two endpoints:
1. `/status`: a health-check route that returns a simple JSON response showing the server is running.
2. `/data`: a data route that reads records from sample_data.csv and returns them as JSON.
3. One Endpoint for homepage on server start: `/`

### Checking Endpoint using CURL Command
1. `/status`: curl -X GET https://symmetrical-adventure-pjgjv7rr6vjgc74j-8000.app.github.dev/status
2. `/data`: curl -X GET https://symmetrical-adventure-pjgjv7rr6vjgc74j-8000.app.github.dev/data

*Command to run server in production:* `gunicorn api-endpoint:app`