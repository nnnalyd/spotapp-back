document.addEventListener('DOMContentLoaded', () => {
    fetch('/user-recommendations')
        .then(response => response.json())
        .then(items => {
            const itemContainer = document.getElementById('items');
            
            items.forEach(item => {
                const itemDiv = document.getElementById('div');
                const itemTitle = document.getElementById('h2');
                const itemImg = document.getElementById('img');

                if (item.type = 'artist'){
                    itemTitle.textContent = item.artist_name;
                    itemImg.src = item.img_url;

                    itemDiv.appendChild(itemTitle);
                    itemDiv.appendChild(itemImg)
                }
                if (item.type = 'track'){
                    itemTitle.textContent = item.track_name;
                    itemImg.src = item.img_url;
                    const itemArtist = document.getElementById('h2');
                    itemArtist.textContent = item.artist_name;
                    const itemPreview = document.getElementById('audio');
                    itemPreview.controls = true;
                    itemPreview.src = item.preview_url;

                    itemDiv.appendChild(itemTitle);
                    itemDiv.appendChild(itemImg);
                    itemDiv.appendChild(itemArtist);
                    itemDiv.appendChild(itemPreview);
                }
            });
        }
        )
})