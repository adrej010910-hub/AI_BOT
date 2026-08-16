# Lead approval dashboard

Static dashboard for reviewing website audit leads and approving outreach drafts.

Run the API from `backend/` and serve this directory with any static web server.

Default API URL: `http://localhost:8000`.

You can override it in the browser console/localStorage:

```js
localStorage.setItem('AI_BOT_API', 'https://your-api.example.com')
```

The dashboard intentionally has no automatic send action yet. `Approve` records approval; an email provider will be connected only after the review workflow is validated.
