import { useState, useEffect, useRef } from 'react'
import { MathfieldElement } from 'mathlive'
import Accordion from 'react-bootstrap/Accordion'
import renderMathInElement from 'katex/dist/contrib/auto-render'

let customMacros = {
  approx: '\\operatorname{approx}',
  factor: '\\operatorname{factor}',
  solve: '\\operatorname{solve}',
  expand: '\\operatorname{expand}',
  lcm: '\\operatorname{lcm}',
  gcd: '\\operatorname{gcd}',
}

function Steps({ data }) {
  if (!data) return
  if (!Array.isArray(data)) return <div>{data}</div>

  return (
    <Accordion alwaysOpen>
      <Accordion.Header>{data[0]}</Accordion.Header>
      <Accordion.Body>
        {data.slice(1).map((s, i) => (
          <Steps key={i} data={s} />
        ))}
      </Accordion.Body>
    </Accordion>
  )
}

function App() {
  const [mathInput, setMathInput] = useState(
    '\\solve{\\left(\\left\\lbrack x^2+11=4y^2,x^2+y=28\\right\\rbrack,x,y\\right)}',
  )

  const [success, setSuccess] = useState(true)
  const [solveTitle, setSolveTitle] = useState('')
  const [mathOutput, _setMathOutput] = useState('')
  const [steps, _setSteps] = useState([])
  const mf = useRef(null)

  const setSteps = (s) => {
    if (!steps) {
      _setSteps(s)
      return
    }
    setSolveTitle(s[0])
    _setSteps(s.slice(1))
    setTimeout(() => renderMathInElement(document.body), 1)
  }

  const setMathOutput = (s) => {
    _setMathOutput(s)
    setTimeout(() => renderMathInElement(document.body), 1)
  }

  useEffect(() => {
    mf.current.macros = { ...mf.current.macros, ...customMacros }
    mf.current.inlineShortcuts = {
      ...mf.current.inlineShortcuts,
      ...Object.fromEntries(
        Object.keys(customMacros).map((k) => [
          k,
          '\\' + k + '{\\left(#1\\right)}',
        ]),
      ),
      root: '\\sqrt[#?]{#1}',
      i: '\\i',
    }
  }, [])

  const evaluate = async () => {
    let resp = await window.pywebview.api.evaluate(mathInput)

    if (resp.error) {
      setSuccess(false)
      setMathOutput(resp.error)
    } else {
      setSuccess(true)
      setMathOutput(resp.final)
    }

    setSteps(resp.steps)
  }

  return (
    <div data-bs-theme='dark'>
      <div className='container mt-3'>
        <math-field
          onChange={(e) => setMathInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && evaluate()}
          ref={mf}
        >
          {mathInput}
        </math-field>
      </div>

      <Accordion defaultActiveKey='0' alwaysOpen flush>
        <Accordion.Item eventKey='0'>
          <Accordion.Header>
            {success ? '✅' : '🚫'} Final Answer
          </Accordion.Header>
          <Accordion.Body
            className={success ? (mathOutput ? 'bg-success' : '') : 'bg-danger'}
          >
            {mathOutput}
          </Accordion.Body>
        </Accordion.Item>
        <Accordion.Item eventKey='1'>
          <Accordion.Header>📘 Steps: {solveTitle}</Accordion.Header>
          <Accordion.Body>
            {steps.map((s, i) => (
              <Steps key={i} data={s} />
            ))}
          </Accordion.Body>
        </Accordion.Item>
      </Accordion>
    </div>
  )
}

export default App
