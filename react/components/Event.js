import React from 'react'
import { render } from 'react-dom'
import io from 'socket.io-client'
import Peer from 'peerjs'
import _ from 'lodash'
import Webcam from 'react-webcam'
import ReactPlayer from 'react-player'

/* global data */

const PORT = process.env.PORT || 3000
const props = JSON.parse(_.unescape(data))

export default class Event extends React.Component {
  constructor () {
    super()
    this.state = {
      isOwner: props.ownerId === props.userId,
      streaming: false,
      player: null,
      in_progress: false,
      socket: null,
      peer: null,
      viewers: 0
    }
  }

  componentWillUnmount () {
    this.state.socket.close()
  }

  async componentDidMount () {
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
      if (isOwner) {
        const peers = {}
        navigator.mediaDevices.getUserMedia({
          video: true,
          audio: true
        }).then(stream => {
          this.setState({
            player: <Webcam audio='false' mirrored='true' />
          })
          socket.on('user-connected', peerId => {
            const call = peer.call(peerId, stream)
            console.log(peerId, 'connected')
            peers[peerId] = call
            this.setState({
              viewers: this.state.viewers + 1
            })
            call.on('close', () => {
              this.setState({
                viewers: this.state.viewers - 1
              })
            })
          })
        })
      } else {
        peer.on('call', (call, id) => {
          console.log('answering call')
          call.answer()
          call.on('stream', stream => {
            console.log('got stream, setting player')
            this.setState({
              player: <ReactPlayer url={stream} playing={true} controls={true} />
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
    return (
      <>
        {this.state.player}
      </>
    )
  }
}

const container = document.querySelector('#react-event')
if (container) render(<Event />, container)
