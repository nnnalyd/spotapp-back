function userRecommendations(){
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
}
function audioPlayer(){
    document.addEventListener('DOMContentLoaded', function () {
        var playButtons = document.querySelectorAll('.play-button');
        playButtons.forEach(function(button) {
            button.addEventListener('click', function() {
                var audioId = this.getAttribute('data-audio-id');
                var audio = document.getElementById(audioId);
                if (audio.paused) {
                    audio.play();
                    this.textContent = 'Pause';
                } else {
                    audio.pause();
                    this.textContent = 'Play';
                }
            });
        });
    });
}

function trackRecommendations(){
    document.addEventListener('DOMContentLoaded', function(){
        fetch('/user-recommendations')
        .then(items => {
            
        })
    })
}