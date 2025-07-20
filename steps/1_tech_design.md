# Technical Design

Use the following workflow to guide your technical design based on the input. 

## Output `tech_design.md`

Create an output file called `tech_design.md` that incorporates the following procedure.

## 1. Identify Application Workload

The first step in the schema design process is to identify the operations that your application runs most frequently.


When you consider your application's workload, consider the scenarios your application currently supports and scenarios it may support in the future. Design your schema to function in all stages of your application development.

### Sub-Steps

#### 1. Identify the data your application needs

To identify the data that your application needs, consider the following factors:

- Your application's users and the information they need.
- Your business domain.
- Application logs and frequently-run queries. To see database commands run on a MongoDB deployment, see Database Profiler.

#### 2. Create a workload table with your application's queries

Fill out the following table with the queries that your application needs to run:

| Action | Query Type | Information | Frequency | Priority |
|--------|------------|-------------|-----------|----------|
| The action that a user takes to trigger the query. | The type of query (read or write). | The document fields that are either written or returned by the query. | How frequently your application runs the query.<br><br>Queries that are run frequently benefit from indexes and should be optimized to avoid lookup operations. | How critical the query is to your application. |

### Example

The following example shows a workload table for a blog application:

| Action | Query Type | Information | Frequency | Priority |
|--------|------------|-------------|-----------|----------|
| Submit a new article | Write | author, text | 10 per day | High |
| Submit a comment on an article | Write | user, text | 1,000 per day (100 per article) | Medium |
| View an article | Read | article id, text, comments | 1,000,000 per day | High |
| View article analytics | Read | article id, comments, clicks | 10 per hour | Low |

## 2. Map Schema Relationships

When you design your schema, consider how your application needs to query and return related data. 

The recommended way to handle related data is to embed it in a sub-document. Embedding related data lets your application query the data it needs with a single read operation and avoid slow `$lookup` operations.

For some use cases, you can use a reference to point to related data in a separate collection.

### About this Task

To determine if you should embed related data or use references, consider the relative importance of the following goals for your application:

1. If your application frequently queries one entity to return data about another entity, embed the data to avoid the need for frequent `$lookup` operations.
2. If your application returns data from related entities together, embed the data in a single collection.
3. If your application frequently updates related data, consider storing the data in its own collection and using a reference to access it. When you use a reference, you reduce your application's write workload by only needing to update the data in a single place.


### Sub-Steps

#### 1. Identify related data in your schema

Identify the data that your application queries and how entities relate to each other.

Consider the operations you identified from your application's workload in the first step of the schema design process. Note the information these operations write and return, and what information overlaps between multiple operations.

#### 2. Create a schema map for your related data

Your schema map should show related data fields and the type of relationship between those fields (one-to-one, one-to-many, many-to-many).

Your schema map can resemble an [entity-relationship model](https://en.wikipedia.org/wiki/Entity%E2%80%93relationship_model).

#### 3. Choose whether to embed related data or use references

The decision to embed data or use references depends on your application's common queries. Review the queries you identified in the [Identify Application Workload](https://mongodb.com/docs/manual/data-modeling/schema-design-process/identify-workload/#std-label-data-modeling-identify-workload) step and use the guidelines mentioned earlier on this page to design your schema to support frequent and critical queries.

Configure your databases, collections, and application logic to match the approach you choose.

### Examples

Consider the following schema map for a blog application:

The following examples show how to optimize your schema for different queries depending on the needs of your application.

### Optimize Queries for Articles

If your application primarily queries articles for information such as title, embed related information in the `articles` collection to return all data needed by the application in a single operation.

The following document is optimized for queries on articles:

```javascript
db.articles.insertOne(
   {
      title: "My Favorite Vacation",
      date: ISODate("2023-06-02"),
      text: "We spent seven days in Italy...",
      tags: [
         {
            name: "travel",
            url: "<blog-site>/tags/travel"
         },
         {
            name: "adventure",
            url: "<blog-site>/tags/adventure"
         }
      ],
      comments: [
         {
            name: "pedro123",
            text: "Great article!"
         }
      ],
      author: {
         name: "alice123",
         email: "alice@mycompany.com",
         avatar: "photo1.jpg"
      }
   }
)
```

### Optimize Queries for Articles and Authors

If your application returns article information and author information separately, consider storing articles and authors in separate collections. This schema design reduces the work required to return author information, and lets you return only author information without including unneeded fields.

In the following schema, the `articles` collection contains an `authorId` field, which is a reference to the `authors` collection.

#### Articles Collection

```javascript
db.articles.insertOne(
   {
      title: "My Favorite Vacation",
      date: ISODate("2023-06-02"),
      text: "We spent seven days in Italy...",
      authorId: 987,
      tags: [
         {
            name: "travel",
            url: "<blog-site>/tags/travel"
         },
         {
            name: "adventure",
            url: "<blog-site>/tags/adventure"
         }
      ],
      comments: [
         {
            name: "pedro345",
            text: "Great article!"
         }
      ]
   }
)
```

#### Authors Collection

```javascript
db.authors.insertOne(
   {
      _id: 987,
      name: "alice123",
      email: "alice@mycompany.com",
      avatar: "photo1.jpg"
   }
)
```

## 3. Apply Design Patterns

Use schema design patterns to optimize your data model based on how your application queries and uses data.

- Handle Computed Values: Perform calculations in the database so results are ready when the client requests data.
- Group Data: Group data into series to improve performance and account for outliers.
- Polymorphic data: Handle variable document fields and data types in a single collection.
- Document and schema versioning: Prepare for schema changes to account for changing technical requirements.
- Archive data: Move old data to a separate location to increase storage and improve performance where data is accessed most frequently.
