## Javascript101 Api-Endpoint
We built a Node.js Express API with several functional endpoints:
1. `/`: The homepage route that returns a welcome message confirming the server is live.
2. `/api`: A basic health-check route that returns a JSON response confirming the API is active.
3. `/api/items/:id`: A dynamic route that captures an ID parameter and returns it in a JSON response.
4. `/api/items`: A POST route that accepts JSON data (like name and price) and returns a success confirmation.

### Checking Endpoint using CURL Command
*Note: Replace `[BASE_URL]` with your specific codespace URL (e.g., https://symmetrical-adventure-pjgjv7rr6vjgc74j-3000.app.github.dev).*

1. **Homepage**: `curl -X GET [BASE_URL]/`
2. **API Status**: `curl -X GET [BASE_URL]/api`
3. **Dynamic Item**: `curl -X GET [BASE_URL]/api/items/123`
4. **Create Item (POST)**: 
   ```bash
   curl -X POST [BASE_URL]/api/items \
   -H "Content-Type: application/json" \
   -d '{"name": "Laptop", "price": 1000}'
