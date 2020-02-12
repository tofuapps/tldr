var app = new Vue({
    el: '#app',
    data: {
        message: 'Hello Vue!'
    }
})

function docReady(fn) {
    // see if DOM is already available
    if (document.readyState === "complete" || document.readyState === "interactive") {
        // call on next available tick
        setTimeout(fn, 1);
    } else {
        document.addEventListener("DOMContentLoaded", fn);
    }
}

docReady(() => {
    let sampleModal = `
        <div class="modal">
            <div class="content">
                <div class="title">
                </div>
                <form>
                    <div class="row">
                    </div>
                    <div class="row submit">
                        <input type="button" value="Ok">
                        <input type="button" value="Cancel">
                    </div>
                </form>
            </div>
        </div>
    `;

    document.getElementById('summarise-btn').onclick = () => {
        let modal = document.createElement('div');
        modal.innerHTML = sampleModal;

        modal.querySelector('input[value="Ok"]').addEventListener('click', () => {
            document.body.removeChild(modal);
        });

        modal.querySelector('input[value="Cancel"]').addEventListener('click', () => {
            document.body.removeChild(modal);
        });

        document.body.appendChild(modal);
    };

});
