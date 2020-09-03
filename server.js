const PORT = process.env.PORT || 3000
if (PORT === 3000) require('dotenv').config('project/.env')
const { google } = require('googleapis')
const express = require('express')
const app = express()
if (PORT === 3000) app.use(require('cors')())
const server = require('http').Server(app)
const proxy = require('express-http-proxy')
const { ExpressPeerServer } = require('peer')

const redirectUris = ['http://localhost:3000', 'https://band-together-momentum.herokuapp.com']
const SCOPES = ['https://www.googleapis.com/auth/calendar']
const oAuth2Client = new google.auth.OAuth2(process.env.GOOGLE_CLIENT_ID, process.env.GOOGLE_CLIENT_SECRET, redirectUris[PORT === 3000 ? 0 : 1])

// Redirect to https if on Heroku
function requireHTTPS (req, res, next) {
  // The 'x-forwarded-proto' check is for Heroku
  if (!req.secure && req.get('x-forwarded-proto') !== 'https' && PORT !== 3000) {
    return res.redirect('https://' + req.get('host') + req.url)
  }
  next()
}

function insertEvent (auth, event) {
  const calendar = google.calendar({ version: 'v3', auth })
  calendar.events.insert({
    calendarId: 'primary',
    resource: event
  })
}

app.use('/calendar', express.json())
app.post('/calendar', (req, res) => {
  const code = req.body.code
  const event = req.body.event
  event.start.dateTime = new Date(event.start.dateTime * 1000)
  event.end.dateTime = new Date(event.end.dateTime * 1000)
  oAuth2Client.getToken(code, (err, credentials) => {
    if (!err) {
      oAuth2Client.setCredentials(credentials)
      insertEvent(oAuth2Client, event)
    }
  })
  res.send(200).send('OK')
})
app.get('/calendar/oauth', (req, res) => {
  const eventId = req.query.eventId
  const authUrl = oAuth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: SCOPES,
    state: JSON.stringify({ eventId: eventId })
  })
  res.status = authUrl ? 200 : 500
  if (authUrl) res.json({ url: authUrl })
})
app.use(requireHTTPS)
app.use('/peer', ExpressPeerServer(server))
app.use('/static/css', express.static('node_modules/antd/dist'))
app.use('/node_modules', express.static('node_modules'))
app.use('/', proxy('http://localhost:8000', {
  proxyReqOptDecorator: (proxyReqOpts, srcReq) => {
    // Modify headers if running on Heroku
    proxyReqOpts.headers['X-Forwarded-Proto'] = PORT === 3000 ? 'http' : 'https'
    proxyReqOpts.headers.Host = PORT === 3000 ? 'localhost:3000' : 'band-together-momentum.herokuapp.com'
    return proxyReqOpts
  },
  limit: '100mb'
}))

server.listen(PORT)
console.log(`Peer server running on port ${PORT}`)
