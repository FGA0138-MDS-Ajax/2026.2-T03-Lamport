import { describe, expect, it } from 'vitest'
import { validateEmail, validateNewPassword } from './validation'

describe('validateEmail', () => {
  it('accepts a valid e-mail', () => {
    expect(validateEmail(' ana@example.com ')).toBeUndefined()
  })

  it.each(['', 'ana', 'ana@', 'ana@example', 'ana @example.com'])('rejects "%s"', (email) => {
    expect(validateEmail(email)).toBeDefined()
  })
})

describe('validateNewPassword', () => {
  it('requires between 8 and 128 characters', () => {
    expect(validateNewPassword('')).toBeDefined()
    expect(validateNewPassword('1234567')).toBeDefined()
    expect(validateNewPassword('12345678')).toBeUndefined()
    expect(validateNewPassword('x'.repeat(129))).toBeDefined()
  })
})
