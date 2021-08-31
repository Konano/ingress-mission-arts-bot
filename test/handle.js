const assert = require('chai').assert
const handle = require('../src/handle')

describe('handle message', () => {
  let msg = {
    message_id: 52,
    from: {
      id: 70648437,
      first_name: 'Miaonster',
      username: 'Miaonster',
      language_code: 'en-CN',
    },
    chat: {
      id: 70648437,
      first_name: 'Miaonster',
      username: 'Miaonster',
      type: 'private',
    },
    date: 1498993846,
    entities: [{ type: 'bot_command', offset: 0, length: 2 }],
  }

  it('should get mission message', () => {
    msg.text = '/q 第二外国语大学'
    const match = msg.text.match(/\/q (.+)/)
    const result = handle(msg, match)
    const expect = '很抱歉没有查到你想找的任务信息，要不要换个姿势呢？'
    assert.equal(result, expect)
  })
})

// obsolete
