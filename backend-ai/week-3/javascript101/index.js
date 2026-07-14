const express = require("express");

const app = express();
const PORT = 3000;

app.use(express.json());

app.use((req, res, next) => {
    console.log(`Incoming request: ${req.method} ${req.url}`);
    next();
});

app.get("/", (req, res) => {
  res.send("Hello from javascript101!");
});

app.get("/api", (req, res) => {
  res.json({
    message: "API is working",
    success: true
  });
});

// GET request to retrieve an item by ID
app.get("/api/items/:id", (req, res) => {
    const itemId = req.params.id;
    res.json({
        message: `You requested item with ID: ${itemId}`,
        id: itemId,
        status: "success"
    })
});

// POST request to create a new item
app.post("/api/items", (req, res) => {
    const newItem = req.body;
    res.status(201).json({
        message: "Item created successfully",
        receiveData: newItem
    })
})

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
