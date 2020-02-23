const elasticsearch = require('elasticsearch');
const rabbitmq = require('amqplib/callback_api');
const envProps = require('./env_props');


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

const TODO_SEARCH_INDEX_NAME = "todos";
const TODO_SEARCH_INDEX_TYPE = "todo";

// Ping the client to be sure Elastic is up
if (client_ping(elasticClient)) {

    // Check if todo index already exists?
    const todoIndexExists = elasticClient.indices.exists({
        index: TODO_SEARCH_INDEX_NAME
    }, function (error, response, status) {
        if (error) {
            console.log(error);
        } else {
            console.log('Todo index exists in Elasticsearch');
        }
    });


    if (!todoIndexExists) {
        // Create a Todos index. If the index has already been created, then this function fails safely
        elasticClient.indices.create({
            index: TODO_SEARCH_INDEX_NAME
        }, function (error, response, status) {
            if (error) {
                console.log('Could not create Todo index in Elasticsearch: ' + error);
            } else {
                console.log('Created Todo index in Elasticsearch');
            }
        });
    }
}

// Messaging Processing ////////////////////////////////////////////////////////////////////////////////////////////////

rabbitmq.connect(envProps.rabbitmqUrl, function (err, connection) {
    connection.createChannel(function (err, channel) {
        const searchIngestionQueue = 'search-ingestion';

        channel.assertQueue(searchIngestionQueue, {durable: true});

        // Get one (1) message, let other search servers grab messages if there are more
        channel.prefetch(1);

        console.log("Waiting for messages in '%s' queue...", searchIngestionQueue);

        channel.consume(searchIngestionQueue, function (msg) {
            const todoTitle = msg.content.toString();
            console.log("Received '%s' todo", todoTitle);

            // Update the search index
            elasticClient.index({
                index: TODO_SEARCH_INDEX_NAME,
                type: TODO_SEARCH_INDEX_TYPE,
                body: {
                    todotext: todoTitle
                }
            }, function (err, resp, status) {
                if (err) {
                    console.log('Could not index ' + todoTitle + ": " + err);
                } else {
                    console.log('Added Todo: [' + todoTitle + '] to Elasticsearch Index');
                }
            });

            setTimeout(function () {
                channel.ack(msg);
            }, 1000); // 1 second

        }, {noAck: false});
    });
});
