# skillfactory_module_F9

The client works as a simple chat, until you use command 'news |category|'

The categories are: sports, cars, food, music. You'll be shown a message on every invalid input starts with 'news '

Correct input will invoke the post request to the <server_url>/news path

The data from the request's body is used to choose the news string that will be output on the client side

In this example the news storage is presented as a python dict with the request's data categories as the keys

The WebSocket options as autoping=True and heartbeat=10.0 are meant to check if the connection is alive, 
as the heartbeat sends 'ping' message, while autoping should response with 'pong' on every 'ping' from client
