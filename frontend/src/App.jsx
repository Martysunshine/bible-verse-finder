import React, { useMemo, useState } from 'react'

const API = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

function countWords(s){
	return (s.trim().match(/[A-Za-zÀ-ž']+/g) || []).length
}

export default function App(){
	const [text, setText] = useState('Yesterday I had a really interesting dream about feeling sunshine on my face. Then I saw a ship with animals like Noah\'s ark, and felt hope for a better tomorrow.')
	const [loading, setLoading] = useState(false)
	const [results, setResults] = useState([])
	const [error, setError] = useState('')
	const [chosen, setChosen] = useState(null)

	const words = useMemo(()=>countWords(text), [text])
	const disabled = words < 10 || loading

	async function recommend(){
		setLoading(true); setError(''); setResults([]); setChosen(null)
		try{
			const r = await fetch(`${API}/recommend`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ text, k: 3, candidates: 40 })
			})
			if(!r.ok){
				const data = await r.json().catch(()=>({detail:r.statusText}))
				throw new Error(data.detail || `HTTP ${r.status}`)
			}
			const data = await r.json()
			setResults(data.results || [])
		}catch(e){ setError(String(e.message || e)) }
		finally{ setLoading(false) }
	}

	return (
		<main>
			<h1>BibleVerse Finder — AI</h1>
			<p>Write at least 10 words describing your situation, feelings, or theme. The AI will suggest relevant passages.</p>

			<textarea
				value={text}
				onChange={e=>setText(e.target.value)}
				rows={6}
				style={{width:'100%', padding:'10px', fontSize:16}}
				placeholder="Describe your context…"
			/>
			<div className="muted">{words} words {words < 10 && '(need at least 10)'}</div>

			<div style={{marginTop:12, display:'flex', gap:8}}>
				<button onClick={recommend} disabled={disabled}>
					{loading? 'Finding passages…' : 'Suggest Passages'}
				</button>
				{chosen != null && results[chosen] && (
					<div className="muted">Selected: {results[chosen].book} {results[chosen].chapter}:{results[chosen].verse}</div>
				)}
			</div>

			{error && <p style={{color:'crimson'}}>{error}</p>}

			<div style={{marginTop:16}}>
				{results.map((r, i)=> (
					<div key={i} className="card" onClick={()=>setChosen(i)} style={{borderColor: chosen===i ? '#888' : '#ddd'}}>
						<div style={{display:'flex', justifyContent:'space-between', gap:8}}>
							<strong>{r.book} {r.chapter}:{r.verse}</strong>
							<span className="muted">relevance: {r.score?.toFixed ? r.score.toFixed(3) : r.score}</span>
						</div>
						<div style={{margin:'6px 0'}}>{r.text}</div>
						<div className="muted">Why: {r.why}</div>
					</div>
				))}
			</div>
		</main>
	)
}