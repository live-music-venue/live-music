const express = require('express')
const app = express()
app.use(require('cors')())
const server = require('http').Server(app)
const proxy = require('express-http-proxy')
const PORT = process.env.PORT || 3001
const io = require('socket.io')(server)
const { ExpressPeerServer } = require('peer')

io.on('connection', socket => {
  console.log('we have socket!')
  console.log(socket)
})
app.use('/peer', ExpressPeerServer(server))
app.use('/', proxy('http://localhost:8000'))

server.listen(PORT)
console.log(`Socket.io / Peer server running on port ${PORT}`)
