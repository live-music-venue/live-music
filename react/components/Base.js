import React from 'react'
import { render } from 'react-dom'
import { PageHeader, Menu, Dropdown, Layout } from 'antd'
import {
  MenuOutlined, HomeOutlined, LogoutOutlined,
  DownOutlined, LoginOutlined, UserAddOutlined,
  ProfileOutlined, StarOutlined, InfoCircleOutlined,
  VideoCameraAddOutlined, AudioOutlined, GlobalOutlined
} from '@ant-design/icons'
import { blue, grey } from '@ant-design/colors'

/* global location isAuthenticated loginURL signupURL logoutURL isMusician username musicianSignupURL profileURL addEventURL favoritesURL mapURL aboutUsURL */

const { Header, Content, Sider } = Layout

function redirect (url) {
  location.href = url
}

const container = document.querySelector('.main-block')
const content = container.innerHTML
console.log(content)

console.log(isMusician)

export default class Base extends React.Component {
  constructor () {
    super()
    this.state = {
      showMenu: false
    }
    this.toggleMenu = this.toggleMenu.bind(this)
  }

  toggleMenu () {
    this.setState({
      showMenu: !this.state.showMenu
    })
  }

  componentDidMount () {
    container.removeAttribute('style')
    document.querySelector('.ant-page-header-heading-title').addEventListener('click', e => {
      redirect('/')
    })
  }

  render () {
    const { toggleMenu } = this
    const { showMenu } = this.state
    let accountMenu = null
    if (isAuthenticated) {
      accountMenu = (
        <Menu>
          <Menu.Item
            icon={<LogoutOutlined />}
            onClick={e => {
              redirect(logoutURL)
            }}
          >
            Log Out
          </Menu.Item>
        </Menu>
      )
    } else {
      accountMenu = (
        <Menu>
          <Menu.Item
            icon={<LoginOutlined />}
            onClick={e => {
              redirect(loginURL)
            }}
          >
            Log In
          </Menu.Item>
          <Menu.Item
            icon={<UserAddOutlined />}
            onClick={e => {
              redirect(signupURL)
            }}
          >
            Sign Up
          </Menu.Item>
        </Menu>
      )
    }
    return (
      <>
        <Layout>
          <Header className='site-layout-background' theme='light' style={{ position: 'fixed', width: '100%', paddingLeft: 7, paddingRight: 0 }}>
            <PageHeader
              title='Band Together'
              subtitle='This is a sample'
              style={{
                height: '100%'
              }}
              theme='light'
              onBack={() => toggleMenu()}
              backIcon={<MenuOutlined style={{ color: showMenu ? blue.primary : grey[0] }} />}
              extra={[
                <Dropdown
                  key='1'
                  overlay={accountMenu}
                >
                  <span className='ant-dropdown-link f5 pointer mt2' style={{ color: blue.primary, userSelect: 'none' }} onClick={e => e.preventDefault()}>{isAuthenticated ? `Welcome, ${username}!` : 'Account'} <DownOutlined /></span>
                </Dropdown>
              ]}
            />
          </Header>
          <Layout className='site-layout' hasSider='true' style={{ marginLeft: showMenu ? 225 : 75, marginTop: 64 }}>
            <Sider
              trigger={null}
              style={{
                overflow: 'auto',
                height: '100vh',
                position: 'fixed',
                left: 0
              }}
              theme='light'
              collapsible
              width={225}
              collapsedWidth={75}
              defaultCollapsed={false}
              collapsed={!showMenu}
              onCollapse={e => toggleMenu()}
            >
              <Menu
                // defaultSelectedKeys={['home']}
                width={75}
                mode='inline'
                theme='light'
              >
                <Menu.Item
                  key='home'
                  icon={<HomeOutlined />}
                  onClick={e => {
                    redirect('/')
                  }}
                >
                  Home
                </Menu.Item>

                {!isMusician && isAuthenticated && (
                  <Menu.Item
                    key='start-streaming'
                    icon={<AudioOutlined />}
                    onClick={e => {
                      redirect(musicianSignupURL)
                    }}
                  >
                    Become a Streamer!
                  </Menu.Item>
                )}

                {isMusician && (
                  <Menu.Item
                    key='profile'
                    icon={<ProfileOutlined />}
                    onClick={e => {
                      redirect(profileURL)
                    }}
                  >
                    Profile
                  </Menu.Item>
                )}

                {isMusician && (
                  <Menu.Item
                    key='add-event'
                    icon={<VideoCameraAddOutlined />}
                    onClick={e => {
                      redirect(addEventURL)
                    }}
                  >
                    Add Event
                  </Menu.Item>
                )}

                {isAuthenticated && (
                  <Menu.Item
                    key='favorites'
                    icon={<StarOutlined />}
                    onClick={e => {
                      redirect(favoritesURL)
                    }}
                  >
                    Favorites
                  </Menu.Item>
                )}

                <Menu.Item
                  key='map'
                  icon={<GlobalOutlined />}
                  onClick={e => {
                    redirect(mapURL)
                  }}
                >
                  Map
                </Menu.Item>

                <Menu.Item
                  key='about'
                  icon={<InfoCircleOutlined />}
                  onClick={e => {
                    redirect(aboutUsURL)
                  }}
                >
                  About Band Together
                </Menu.Item>

                {!isAuthenticated && (
                  <Menu.Item
                    key='login-side'
                    icon={<LoginOutlined />}
                    onClick={e => {
                      redirect(loginURL)
                    }}
                  >
                    Login
                  </Menu.Item>
                )}

                {!isAuthenticated && (
                  <Menu.Item
                    key='signup-side'
                    icon={<UserAddOutlined />}
                    onClick={e => {
                      redirect(signupURL)
                    }}
                  >
                    Register
                  </Menu.Item>
                )}

                {isAuthenticated && (
                  <Menu.Item
                    key='logout-side'
                    icon={<LogoutOutlined />}
                    onClick={e => {
                      redirect(logoutURL)
                    }}
                  >
                    Logout
                  </Menu.Item>
                )}

              </Menu>
            </Sider>
            <Content style={{ margin: '0 16px 0', height: '100%', overflow: 'initial' }}>
              <div dangerouslySetInnerHTML={{ __html: content }} />
            </Content>
          </Layout>
        </Layout>
      </>
    )
  }
}

if (container) render(<Base />, container)
