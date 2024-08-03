document.addEventListener('DOMContentLoaded', function() {
    const generateBtn = document.getElementById('generateBtn');
    const moodInput = document.getElementById('moodText');
    const resultDiv = document.getElementById('result');
    const spotifyPlayerDiv = document.getElementById('spotifyPlayer');
    const coverArtDiv = document.getElementById('coverArt');
    const themeToggle = document.getElementById('themeToggle');
    const addToSpotifyBtn = document.getElementById('addToSpotifyBtn');

    generateBtn.addEventListener('click', generatePlaylist);
    themeToggle.addEventListener('click', toggleTheme);
    addToSpotifyBtn.addEventListener('click', addToSpotify);

    function toggleTheme() {
        const html = document.documentElement;
        if (html.getAttribute('data-theme') === 'light') {
            html.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
        } else {
            html.setAttribute('data-theme', 'light');
            localStorage.setItem('theme', 'light');
        }
    }

    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);

    async function generatePlaylist() {
        const mood = moodInput.value.trim();
        if (!mood) return;

        resultDiv.innerHTML = 'Generating playlist...';
        spotifyPlayerDiv.innerHTML = '';
        coverArtDiv.innerHTML = '';
        addToSpotifyBtn.style.display = 'none';

        try {
            const response = await fetch('/generate_playlist', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ mood: mood })
            });

            if (!response.ok) {
                throw new Error('Failed to generate playlist');
            }

            const data = await response.json();
            displayPlaylist(data.playlist, data.trackUris);
            addToSpotifyBtn.style.display = 'block';
        } catch (error) {
            console.error('Error:', error);
            resultDiv.innerHTML = 'An error occurred. Please try again.';
        }
    }

    function displayPlaylist(playlist, trackUris) {
        if (!playlist || playlist.length === 0) {
            resultDiv.innerHTML = 'No songs found for this mood.';
            return;
        }

        let resultHtml = '<h3>Your Personalized Playlist:</h3><ul>';
        playlist.forEach(track => {
            resultHtml += `<li>${track.name} by ${track.artists[0].name}</li>`;
            if (track.album.images && track.album.images.length > 0) {
                const coverUrl = track.album.images[0].url;
                const trackUrl = track.external_urls.spotify;
                coverArtDiv.innerHTML += `<a href="${trackUrl}" target="_blank"><img src="${coverUrl}" alt="Album Cover"></a>`;
            }
        });
        resultHtml += '</ul>';
        resultDiv.innerHTML = resultHtml;

        // Store the trackUris for later use
        addToSpotifyBtn.dataset.trackUris = JSON.stringify(trackUris);
    }

    async function addToSpotify() {
        const trackUris = JSON.parse(addToSpotifyBtn.dataset.trackUris);
        const mood = moodInput.value.trim();

        try {
            const response = await fetch('/create_spotify_playlist', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ trackUris: trackUris, mood: mood })
            });

            if (!response.ok) {
                throw new Error('Failed to create playlist');
            }

            const data = await response.json();
            if (data.success) {
                spotifyPlayerDiv.innerHTML = `
                    <iframe
                        src="https://open.spotify.com/embed/playlist/${data.playlistId}"
                        width="100%"
                        height="380"
                        frameborder="0"
                        allowtransparency="true"
                        allow="encrypted-media">
                    </iframe>
                `;
                addToSpotifyBtn.style.display = 'none';
            } else if (data.authUrl) {
                // Redirect to Spotify authorization
                window.location.href = data.authUrl;
            } else {
                throw new Error('Failed to create playlist');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while creating the playlist. Please try again.');
        }
    }
});