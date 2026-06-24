import { useState, useEffect } from 'react'
import API from '../api/auth'
import { Loading } from '../components/KpiCard'
import { FiFileText, FiDownload } from 'react-icons/fi'

export default function Reports() {
  const [reports, setReports] = useState([])
  const [datasets, setDatasets] = useState([])
  const [loading, setLoading] = useState(true)

  const fetchAll = async () => {
    try {
      const [rRes, dRes] = await Promise.all([
        API.get('/export/reports'),
        API.get('/upload/datasets')
      ])
      setReports(rRes.data)
      setDatasets(dRes.data.filter(d => d.status === 'ready'))
    } catch {}
    setLoading(false)
  }

  useEffect(() => { fetchAll() }, [])

  const exportUrl = (id, type) => {
    const token = localStorage.getItem('token')
    return `/api/export/${id}/${type}?token=${token}`
  }

  return (
    <div>
      <div className="page-header">
        <h2>Reports & Exports</h2>
        <p>Download reports and export processed data</p>
      </div>

      <div className="table-card">
        <h3>Export Dataset Reports</h3>
        {loading ? <Loading /> :
          datasets.length === 0 ? (
            <div className="empty-state"><div className="icon">📋</div><p>No ready datasets found</p></div>
          ) : (
            <table>
              <thead>
                <tr><th>Dataset</th><th>Rows</th><th>Uploaded</th><th>Actions</th></tr>
              </thead>
              <tbody>
                {datasets.map(ds => (
                  <tr key={ds.id}>
                    <td><FiFileText style={{marginRight:'.5rem', color:'#2563eb'}} />{ds.filename}</td>
                    <td>{ds.row_count?.toLocaleString()}</td>
                    <td>{new Date(ds.uploaded_at).toLocaleDateString()}</td>
                    <td>
                      <div style={{display:'flex', gap:'.5rem'}}>
                        <a href={exportUrl(ds.id, 'csv')} target="_blank" className="btn btn-secondary btn-sm">
                          <FiDownload size={13} /> CSV
                        </a>
                        <a href={exportUrl(ds.id, 'pdf')} target="_blank" className="btn btn-primary btn-sm">
                          <FiDownload size={13} /> PDF
                        </a>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )
        }
      </div>

      <div className="table-card">
        <h3>Saved Reports</h3>
        {loading ? <Loading /> :
          reports.length === 0 ? (
            <div className="empty-state">
              <div className="icon">📄</div>
              <p>No saved reports yet. Use the dashboard to generate insights.</p>
            </div>
          ) : (
            <table>
              <thead><tr><th>Report Name</th><th>Created</th></tr></thead>
              <tbody>
                {reports.map(r => (
                  <tr key={r.id}>
                    <td><FiFileText style={{marginRight:'.5rem', color:'#7c3aed'}} />{r.name}</td>
                    <td>{new Date(r.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )
        }
      </div>
    </div>
  )
}
