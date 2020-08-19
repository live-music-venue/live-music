import React from 'react'
import { render } from 'react-dom'
import io from 'socket.io-client'
import Peer from 'peerjs'
import _ from 'lodash'
import Webcam from 'react-webcam'
import ReactPlayer from 'react-player'

/* global data isAuthenticated */

const PORT = Number(window.location.port)
let props = {}

export default class Event extends React.Component {
  constructor () {
    super()
    props = JSON.parse(_.unescape(data))
    this.state = {
      isOwner: props.ownerId === props.userId,
      streaming: false,
      player: null,
      in_progress: false,
      socket: null,
      peer: null,
      viewers: 0,
      chat: [],
      message: ''
    }
  }

  componentWillUnmount () {
    this.state.socket.close()
  }

  async componentDidMount () {
    console.log(PORT)
    await this.setState({
      socket: io(`http://localhost:${PORT}`),
      peer: new Peer({
        host: 'localhost',
        port: PORT,
        path: '/peer',
        secure: PORT !== 3000
      })
    })
    const { socket, peer, isOwner } = this.state
    peer.on('open', id => {
      socket.emit('join_event', props.pk, props.userId, id)
      socket.on('update-viewer-count', viewerCount => {
        this.setState({
          viewers: viewerCount
        })
      })
      socket.on('recieve-chat-message', (data) => {
        const chat = document.querySelector('#chat')
        this.setState({
          chat: this.state.chat.concat(<p>{`${data.username}: ${data.message}`}</p>)
        })
        chat.scrollTop = chat.scrollHeight
      })
      if (isOwner) {
        const peers = {}
        navigator.mediaDevices.getUserMedia({
          video: true,
          audio: true
        }).then(stream => {
          this.setState({
            viewers: 0,
            player: <Webcam audio='false' mirrored='true' />
          })
          socket.on('user-connected', peerId => {
            const call = peer.call(peerId, stream)
            peers[peerId] = call
            socket.on('user-disconnected', peerId => {
              if (peers[peerId]) peers[peerId].close()
              delete peers[peerId]
            })
          })
        })
      } else {
        peer.on('call', (call, id) => {
          call.answer()
          call.on('stream', stream => {
            this.setState({
              player: <ReactPlayer url={stream} playing='true' controls='true' />
            })
          })
          call.on('close', () => {
            socket.close()
          })
        })
      }
    })
    window.addEventListener('beforeunload', e => {
      socket.close()
    })
  }

  render () {
    const { viewers, player, socket, chat, message } = this.state
    return (
      <>
        <p>{viewers} Viewer{viewers !== 1 && 's'}</p>
        <div className='flex'>
          {player}
          <div>
            <div id='chat' className='pre' style={{ width: 300, height: 200 }}>
              {chat.map(msg => {
                return msg
              })}
            </div>
            <input
              type='text'
              value={message}
              onChange={e => {
                this.setState({
                  message: e.target.value
                })
              }}
            />
            <button
              onClick={e => {
                if (isAuthenticated) socket.emit('send_message', message)
                this.setState({
                  message: ''
                })
              }}
            >
              Send
            </button>
          </div>
        </div>
      </>
    )
  }
}

const container = document.querySelector('#react-event')
if (container) render(<Event />, container)
