// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';

// Polyfill for CRA's older jsdom test environment, which doesn't provide
// TextEncoder/TextDecoder globally. react-router v7 needs these.
import { TextEncoder, TextDecoder } from 'util';
if (typeof global.TextEncoder === 'undefined') {
  global.TextEncoder = TextEncoder;
  global.TextDecoder = TextDecoder;
}
