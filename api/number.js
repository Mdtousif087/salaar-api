import { google } from 'googleapis';

export default async function handler(req, res) {
  const { number } = req.query;

  if (!number) {
    return res.status(400).json({ error: 'Number parameter required' });
  }

  try {
    const auth = new google.auth.GoogleAuth({
      credentials: {
        client_email: process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL,
        private_key: process.env.GOOGLE_PRIVATE_KEY?.replace(/\\n/g, '\n'),
      },
      scopes: ['https://www.googleapis.com/auth/drive.readonly'],
    });

    const drive = google.drive({ version: 'v3', auth });
    
    const results = [];
    const fileIds = [
      process.env.GOOGLE_DRIVE_FILE_ID_1,  // database1.csv
      process.env.GOOGLE_DRIVE_FILE_ID_2,  // database2.csv  
      process.env.GOOGLE_DRIVE_FILE_ID_3   // database.csv
    ];

    // Teenon files check karo
    for (const fileId of fileIds) {
      if (!fileId) continue; // Skip if file ID not set
      
      try {
        const response = await drive.files.get({
          fileId: fileId,
          alt: 'media',
        });

        const csvText = response.data;
        const lines = csvText.split('\n');
        const headers = lines[0].split(',').map(h => h.trim());
        
        for (let i = 1; i < lines.length; i++) {
          if (lines[i].trim()) {
            const values = lines[i].split(',');
            const record = {};
            headers.forEach((header, index) => {
              record[header] = values[index] ? values[index].trim() : '';
            });
            
            // Mobile ya alt number match kare to add karo
            if (record.mobile === number || record.alt === number) {
              results.push({
                ...record,
                source_file: `database${fileIds.indexOf(fileId) + 1}.csv`
              });
            }
          }
        }
      } catch (fileError) {
        console.error(`Error reading file ${fileId}:`, fileError);
        // Continue with next file
      }
    }

    if (results.length === 0) {
      return res.status(404).json({ error: 'Number not found in any database' });
    }

    // Response format
    res.status(200).json({
      search_number: number,
      total_results: results.length,
      results: results
    });

  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: 'Internal server error: ' + error.message });
  }
}
