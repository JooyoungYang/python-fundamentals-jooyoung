db = db.getSiblingDB('dataeng');


db.users.insertMany([
  {
    username: "alice",
    email: "alice@example.com",
    profile: {
      age: 28,
      city: "Berlin",
      interests: ["python", "data science"]
    },
    created_at: new Date()
  },
  {
    username: "bob",
    email: "bob@example.com",
    profile: {
      age: 31,
      city: "Hamburg",
      interests: ["mongodb"]
    },
    created_at: new Date()
  }
]);


db.users.createIndex({ username: 1 }, { unique: true });

console.log("MongoDB initialized with sample data");