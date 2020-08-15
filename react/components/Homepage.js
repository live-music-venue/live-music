import React from 'react'
import { render } from 'react-dom'

export default class Homepage extends React.Component {
  render () {
    return (
      <>
        <h1>Hello</h1>
        <p>This is a react component</p>
      </>
    )
  }
}

render(<Homepage />, document.getElementById('react-homepage'))
