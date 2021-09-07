

function captionsalign() {
    let allcues = document.querySelector('#caption').track.cues;
    for (let i =0; i < allcues.length; i++) {
        allcues[i].line = 14;
    }
};

captionsalign();