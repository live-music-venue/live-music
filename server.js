const express = require('express')
const app = express()
app.use(require('cors')())
const server = require('http').Server(app)
const proxy = require('express-http-proxy')
const PORT = process.env.PORT || 3000
const { ExpressPeerServer } = require('peer')

app.use('/peer', ExpressPeerServer(server))
app.use('/', proxy('http://localhost:8000'))

server.listen(PORT)
console.log(`Peer server running on port ${PORT}`)
