function fillTile(tile, letter) {
    tile.innerHTML = letter;
    tile.setAttribute("data-state", "tbd");
}

function emptyTile(tile) {
    tile.innerHTML = null;
    tile.setAttribute("data-state", "empty");
}

function addLetter(self) {
    const letter = self.innerHTML;
    const tbd_tiles = document.querySelectorAll('.Tile-module_tile[data-state="tbd"]');
    var empty_tile = document.querySelectorAll('.Tile-module_tile[data-state="empty"]')[0];
    if (tbd_tiles.length > 0) {
        const tbd_tile = tbd_tiles[tbd_tiles.length - 1];
        const tbd_row = parseInt(tbd_tile.getAttribute("grid-index-row"));
        const empty_row = parseInt(empty_tile.getAttribute("grid-index-row"));
        if (tbd_row == empty_row) {
            fillTile(empty_tile, letter);
        }
    } else {
        fillTile(empty_tile, letter);
    }
}

function removeLetter() {
    const tbd_tiles = document.querySelectorAll('.Tile-module_tile[data-state="tbd"]');
    if (tbd_tiles.length > 0) {
        emptyTile(tbd_tiles[tbd_tiles.length - 1]);
    }
}

function postToBackendRedirect(url, body) {
    fetch(
        url,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(body),
            redirect: "follow"
        }
    )
        .then(res => {
            if (res.redirected) {
                window.location.href = res.url;
                return;
            }
            else
                return res.text();
        })
        .then(data => {
            document.getElementById("response").innerHTML = data;
        })
        .catch(error => {
            console.error(error);
        });
}

function rowEmpty() {
    const empty_tile_rows = document.querySelectorAll('.Tile-module_tile[data-state="empty"]');
    if (empty_tile_rows.length > 0) {
        return empty_tile_rows[0].getAttribute("grid-index-row");
    }
    return null;
}

function rowTbd() {
    const tbd_tile_rows = document.querySelectorAll('.Tile-module_tile[data-state="tbd"]');
    if (tbd_tile_rows.length > 0) {
        return tbd_tile_rows[tbd_tile_rows.length - 1].getAttribute("grid-index-row");
    }
    return null;
}

function rowFull() {
    const empty_row = rowEmpty();
    const tbd_row = rowTbd();
    return (empty_row - 1) == tbd_row || (empty_row == null && tbd_row != null);
}

function lastWordTiles() {
    if (rowFull()) {
        const tbd_row = rowTbd();
        const filled_tiles = document.querySelectorAll('.Tile-module_tile[grid-index-row="' + tbd_row + '"]');
        return [...filled_tiles];
    }
    return [];
}

function lastWord() {
    const tiles = lastWordTiles();
    let data = [];
    for (let i = 0; i < tiles.length; i++) {
        data.push(tiles[i].innerHTML);
    }
    return data.join('');
}

async function wrongWordAnimation() {
    const tiles = lastWordTiles();
    for (let i = 0; i < tiles.length; i++) {
        tiles[i].removeAttribute("animation_key");
        tiles[i].removeAttribute("style");
    }
    await new Promise(r => setTimeout(r, 100));
    for (let i = 0; i < tiles.length; i++) {
        tiles[i].setAttribute("animation_key", "wrong_word");
        tiles[i].setAttribute("style", "animation-delay:" + (0.1 * i) + "s");
    }
}

async function checkWord() {
    if (rowFull()) {
        console.log("row is full");
        const word = lastWord();
        console.log(word);
        fetch(
            "/board/check_word",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ "last_word": word }),
                redirect: "follow"
            }
        )
            .then(res => {
                if (res.redirected) {
                    window.location.href = res.url;
                    return;
                }
                else {
                    wrongWordAnimation();
                    return;
                }
            })
            .then(data => {
                document.getElementById("response").innerHTML = data;
            })
            .catch(error => {
                console.error(error);
            });
    }
}