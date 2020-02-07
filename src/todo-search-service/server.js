const express = require('express');
const bodyParser = require('body-parser');
const elasticsearch = require('elasticsearch');
const envProps = require('./env_props');

/////// Test curl /////////////////////////////////////////////////////////////////////////
// curl --data "searchText=kids" http://localhost:3002/api/v1/search
///////////////////////////////////////////////////////////////////////////////////////////

// Initializing the Express Framework //////////////////////////////////////////////////////////////////////////////////
const app = express();
const port = 3000;
app.use(bodyParser.json());
app.use(
    bodyParser.urlencoded({
        extended: true
    })
);

function client_ping(client) {
    // Ping the client to be sure Elastic is up
    client.ping({
        requestTimeout: 30000,
    }, function (error) {
        if (error) {
            console.error('Something went wrong with Elasticsearch: ' + error);
            return false;
        } else {
            console.log('Elasticsearch client connected');
            return true;
        }
    });
}

// Elasticsearch Client Setup //////////////////////////////////////////////////////////////////////////////////////////
function try_elastic_connect() {

    let client;
    client = new elasticsearch.Client({
        hosts: [envProps.elasticHost]
    });
    if (!client_ping(client)) {
        client = new elasticsearch.Client({
            hosts: [envProps.elasticHost + ':' + envProps.elasticPort]
        });
    }
    return client;
}

const elasticClient = try_elastic_connect();

// Ping the client to be sure Elastic is up
client_ping(elasticClient);

// Set up the API routes ///////////////////////////////////////////////////////////////////////////////////////////////

const TODO_SEARCH_INDEX_NAME = "todos";
const TODO_SEARCH_INDEX_TYPE = "todo";

// Search all todos
app.route('/api/v1/search').post((req, res) => {
    const searchText = req.body.searchText;

    console.log('CALLED POST api/v1/search with searchText=' + searchText);

    // Perform the actual search passing in the index, the search query and the type
    elasticClient.search({
        index: TODO_SEARCH_INDEX_NAME,
        type: TODO_SEARCH_INDEX_TYPE,
        body: {
            query: {
                match: {
                    todotext: searchText
                }
            }
        }
    })
        .then(results => {
            console.log('Search for "' + searchText + '" matched (' + results.hits.hits.length + ')');
            res.send(results.hits.hits);
        })
        .catch(err => {
            console.log(err);
            res.send([]);
        });
});


// Start the server ////////////////////////////////////////////////////////////////////////////////////////////////////
app.listen(port, () => {
    console.log('Todo Search Service started!');
});

