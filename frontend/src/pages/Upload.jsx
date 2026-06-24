import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import API from '../api/auth'
import { FiUploadCloud, FiFile, FiCheckCircle, FiAlertCircle, FiPlay } from 'react-icons/fi'
import { Loading } from '../components/KpiCard'

export default function Upload() {
  const [dragOver, setDragOver] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [datasets, setDatasets] = useState([])
  const [loadingDatasets, setLoadingDatasets] = useState(true)
  const [progress, setProgress] = useState(0)
  const fileRef = useRef()
  const navigate = useNavigate()

  const fetchDatasets = async () => {
    try {
      const { data } = await API.get('/upload/datasets')
      setDatasets(data)
    } catch {}
    setLoadingDatasets(false)
  }

  useEffect(() => { fetchDatasets() }, [])

  const handleFile = async file => {
    if (!file) return
    const allowed = ['text/csv', 'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
    if (!allowed.includes(file.type) && !file.name.match(/\.(csv|xlsx|xls)$/i)) {
      toast.error('Only CSV or Excel files are allowed')
      return
    }
    const formData = new FormData()
    formData.append('file', file)
    setUploading(true); setProgress(10)
    try {
      const token = localStorage.getItem('token')
      const { data } = await API.post('/upload/', formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          // Do NOT set Content-Type manually — let browser set it with boundary
        },
        onUploadProgress: e => setProgress(Math.round(e.loaded / e.total * 60) + 10)
      })
      setProgress(80)
      toast.success('File uploaded! Processing in background...')
      // Poll for status
      let attempts = 0
      const poll = setInterval(async () => {
        attempts++
        const { data: status } = await API.get(`/upload/datasets/${data.dataset_id}/status`)
        if (status.status === 'ready') {
          clearInterval(poll); setProgress(100)
          toast.success(`✅ ${status.row_count} rows processed!`)
          fetchDatasets()
          setTimeout(() => { setUploading(false); setProgress(0) }, 500)
        } else if (status.status === 'error') {
          clearInterval(poll)
          toast.error('Processing failed. Check your file format.')
          setUploading(false); setProgress(0)
        } else if (attempts > 60) {
          clearInterval(poll)
          toast.error('Processing timeout')
          setUploading(false); setProgress(0)
        }
      }, 2000)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Upload failed')
      setUploading(false); setProgress(0)
    }
  }

  const statusIcon = s => s === 'ready' ? <FiCheckCircle color="#16a34a" /> :
    s === 'error' ? <FiAlertCircle color="#dc2626" /> : <div className="loading-spinner" style={{width:16,height:16}} />

  return (
    <div>
      <div className="page-header">
        <h2>Upload Sales Data</h2>
        <p>Upload CSV or Excel files with sales data. Required columns: Order ID, Order Date, Ship Date, Customer Name, Segment, Region, Category, Sub-Category, Product Name, Sales, Quantity, Discount, Profit</p>
      </div>

      <div
        className={`upload-zone ${dragOver ? 'drag-over' : ''}`}
        onClick={() => !uploading && fileRef.current.click()}
        onDragOver={e => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={e => { e.preventDefault(); setDragOver(false); handleFile(e.dataTransfer.files[0]) }}
      >
        <input ref={fileRef} type="file" accept=".csv,.xlsx,.xls" hidden
          onChange={e => handleFile(e.target.files[0])} />
        <div className="upload-icon">
          {uploading ? '⏳' : <FiUploadCloud style={{fontSize:'3rem', color:'#2563eb'}} />}
        </div>
        <h3>{uploading ? 'Processing your file...' : 'Drop your file here or click to browse'}</h3>
        <p>{uploading ? `${progress}% complete` : 'Supports CSV, Excel (.xlsx, .xls)'}</p>
        {uploading && (
          <div className="upload-progress">
            <div className="upload-progress-bar" style={{ width: `${progress}%` }} />
          </div>
        )}
      </div>

      <div className="dataset-list">
        <h3>Your Datasets</h3>
        {loadingDatasets ? <Loading /> :
          datasets.length === 0 ? (
            <div className="empty-state"><div className="icon">📂</div><p>No datasets uploaded yet</p></div>
          ) : datasets.map(ds => (
            <div key={ds.id} className="dataset-item" onClick={() => ds.status === 'ready' && navigate('/dashboard', { state: { datasetId: ds.id } })}>
              <div className="dataset-icon"><FiFile /></div>
              <div className="dataset-info">
                <div className="filename">{ds.filename}</div>
                <div className="meta">
                  {ds.row_count ? `${ds.row_count.toLocaleString()} rows · ` : ''}
                  {new Date(ds.uploaded_at).toLocaleDateString()}
                </div>
              </div>
              <div style={{display:'flex', alignItems:'center', gap:'.5rem'}}>
                {statusIcon(ds.status)}
                <span className={`badge ${ds.status === 'ready' ? 'badge-green' : ds.status === 'error' ? 'badge-red' : 'badge-orange'}`}>
                  {ds.status}
                </span>
                {ds.status === 'ready' && (
                  <button className="btn btn-primary btn-sm" onClick={e => { e.stopPropagation(); navigate('/dashboard', { state: { datasetId: ds.id } }) }}>
                    <FiPlay size={12} /> Analyze
                  </button>
                )}
              </div>
            </div>
          ))
        }
      </div>
    </div>
  )
}
