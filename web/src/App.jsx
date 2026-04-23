import { useState, useEffect, useRef } from 'react'

import { MathfieldElement } from 'mathlive'
import renderMathInElement from 'katex/dist/contrib/auto-render'
import 'katex/dist/contrib/copy-tex'

let customMacros = ['solve', 'subs', 'factor', 'expand', 'approx', 'lcm', 'gcd']

function Steps({ data, p }) {
  if (!data) return
  if (!Array.isArray(data) || data.length == 0) return data
  const border = data.length > 1 && p ? 'border shadow ' : ''

  return (
    <div
      class={border + 'rounded p-2 mb-2 overflow-auto width-fit'}
      style={{ background: '#1e293b' }}
    >
      {data.map((s, i) => (
        <Steps key={i} data={s} p={data.length > 2} />
      ))}
    </div>
  )
}

function App() {
  // \solve{\left([xy=z,x+y=-7,x+z=-3y-1]\right)}
  const [mathInput, setMathInput] = useState('')

  const [history, setHistory] = useState([])
  const mf = useRef(null)
  const bottomRef = useRef(null)

  useEffect(() => {
    mf.current.macros = {
      ...mf.current.macros,
      ...Object.fromEntries(
        customMacros.map((k) => [k, '\\mathrm{' + k + '}']),
      ),
    }
    mf.current.inlineShortcuts = {
      ...mf.current.inlineShortcuts,
      ...Object.fromEntries(
        customMacros.map((k) => [k, '\\' + k + '{\\left(#1\\right)}']),
      ),
      root: '\\sqrt[#?]{#1}',
      i: '\\mathrm{i}',
    }
  }, [])

  useEffect(() => {
    setTimeout(
      () => bottomRef.current?.scrollIntoView({ behavior: 'smooth' }),
      10,
    )
  }, [history])

  const evaluate = async () => {
    if (!mathInput.trim()) return
    let resp = await window.pywebview.api.evaluate(mathInput)
    setHistory(
      history.concat({
        input: '\\(' + mathInput + '\\)',
        ...resp,
      }),
    )
    setMathInput('')
    setTimeout(
      () =>
        renderMathInElement(document.body, {
          fleqn: true,
          macros: Object.fromEntries(
            customMacros.map((k) => ['\\' + k, '\\mathrm{' + k + '}']),
          ),
          displayMode: false,
        }),
      1,
    )
  }

  return (
    <div data-bs-theme='dark' className='mb-5'>
      {!history.length && <h1>Algebra Engine</h1>}
      <div className='overflow-auto p-2'>
        {history.map((item, i) => (
          <div key={i} className='mb-3'>
            <div
              className='text-end overflow-auto rounded'
              ref={i + 1 == history.length ? bottomRef : null}
            >
              <span className='badge bg-secondary fs-6'>{item.input}</span>
            </div>
            <div className='mt-1'>
              <div
                className={
                  (item.success ? 'bg-success' : 'bg-danger') +
                  ' overflow-auto width-fit border mt-3 mb-1 rounded p-2 shadow text-center'
                }
              >
                {item.output}
              </div>
              <Steps data={item.steps} p={true} />
            </div>
          </div>
        ))}
      </div>

      <div
        className={
          history.length < 1
            ? 'position-fixed top-50 start-50 translate-middle w-75'
            : 'fixed-bottom m-5 w-75 mx-auto'
        }
      >
        <math-field
          onChange={(e) => setMathInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && evaluate()}
          placeholder='\text{Enter math here...}'
          ref={mf}
        >
          {mathInput}
        </math-field>
      </div>
    </div>
  )
}

export default App
