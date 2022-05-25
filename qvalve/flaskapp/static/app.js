// qvalve/flaskapp/static/app.js
//------------------------------------------------------------------------------

function add_event_listener(servers_table) {

    servers_table.addEventListener('click', (e) => {

        // Single-click on <tr class='server'> to show/hide its players.
        // Single-click on <tr class='players'> to refresh server and its players.
        // Ctrl-click on either row to connect.
        // Server is always refreshed.

        e.preventDefault()

        let server_row = null
        let players_row = null

        let clicked_row = e.target.parentNode
        while (clicked_row.parentNode.parentNode != servers_table) {
            clicked_row = clicked_row.parentNode
        }

        if (clicked_row.classList.contains('server')) {
            server_row = clicked_row
        }
        else if (clicked_row.classList.contains('players')) {
            players_row = clicked_row
            server_row = players_row.previousSibling
        }

        if (e.ctrlKey) { // on either row
            connect(server_row)
        }
        else if (clicked_row.classList.contains('server')) {
            players_row = toggle_players(server_row)
        }

        refresh(server_row, players_row)
    })
}

//------------------------------------------------------------------------------

function connect(server_row) {
    // Request creation of tf2 exec script having CONNECT command
    // to the server; map and server names are ECHO'ed for readability.
    // ? use PUT ?

    fetch(url_for(server_row, '/connect'))
        .catch((error) => console.log(error))

    // mark the last server connected to
    for (row = server_row.parentNode.firstElementChild ; row ; ) {
        row.removeAttribute('_connected')
        row = row.nextElementSibling
    }
    server_row.setAttribute('_connected', 'true')
}

//------------------------------------------------------------------------------

function toggle_players(server_row) {
    // Toggle display of players on and off.
    //
    // If switched on, insert new player_row beneath server_row.
    // Return new player_row.
    //
    // If switched off, remove player_row.
    // Return null.

    if (server_row.hasAttribute('_has_players_row')) {
        server_row.removeAttribute('_has_players_row')
        let idx = server_row.rowIndex + 1
        server_row.parentNode.parentNode.deleteRow(idx)
        return null
    }

    // indicate presence of player row
    server_row.setAttribute('_has_players_row', 'true')

    // create new row beneath server row
    let player_row = insertAfter(document.createElement('tr'), server_row)

    // same address
    player_row.setAttribute('addr', server_row.getAttribute('addr'))

    // use same classes as server row, with one change.
    player_row.classList = server_row.classList
    player_row.classList.replace('server', 'players')

    // make the players appear indented by skipping a few columns
    let td = player_row.insertCell(0)
    td.colSpan = 10
    td = player_row.insertCell(1)
    td.colSpan = 4
    td.width = '100%'
    td.appendChild(document.createElement(null))

    return player_row
}

//------------------------------------------------------------------------------

function refresh(server_row, players_row) {
    // Fetch and display server data, and (optionally) players data.

    fetch(url_for(server_row, '/show-players'))
        // `qvalve.gameserver.GameServer` object
        .then((response) => response.json())
        .then((server) => {
            // render_server
            server_row.cells[8].innerText = server['ping']
            server_row.cells[9].innerText = server['players']
            server_row.cells[10].innerText = server['max_players']
            server_row.cells[11].innerText = server['bots']
            server_row.cells[12].innerText = server['map_name']
            if (players_row) {
                td = players_row.cells[1]
                td.replaceChild(render_players(server), td.firstChild)
            }
        })
        .catch((error) => console.log(error))
}

//------------------------------------------------------------------------------

function render_players(server) {
    // Render server's players.

    let table = document.createElement('table')
    table.className = 'table table-sm table-condensed table-bordered a2s_players'

    let playerno = 0
    server.a2s_players.forEach((player) => {

        playerno += 1
        let tr = document.createElement('tr')
        table.appendChild(tr)

        //
        let td = document.createElement('td')
        tr.appendChild(td)
        td.appendChild(document.createTextNode(playerno))
        td.className = 'text-right'

        //
        td = document.createElement('td')
        tr.appendChild(td)
        let time = new Date(player.duration * 1000).toISOString().substr(11, 8)
        td.appendChild(document.createTextNode(time))
        td.className = 'text-right'

        //
        td = document.createElement('td')
        tr.appendChild(td)
        td.appendChild(document.createTextNode(player.score))
        td.className = 'text-right'

        //
        td = document.createElement('td')
        tr.appendChild(td)
        td.appendChild(document.createTextNode(player.attributes))

        //
        td = document.createElement('td')
        tr.appendChild(td)
        td.appendChild(document.createTextNode(player.name))
        td.width = '100%'
    })

    return table
}

//------------------------------------------------------------------------------

function url_for(server_row, path) {

    let addr = server_row.getAttribute('addr')
    let map_name = server_row.cells[server_row.cells.length-2].innerText
    let server_name = server_row.cells[server_row.cells.length-1].innerText
    let params = new URLSearchParams({map_name: map_name, server_name: server_name})

    return `${path}/${addr}?${params}`
}

//------------------------------------------------------------------------------

function insertAfter(newNode, referenceNode) {
    // Return inserted node.
	return referenceNode.parentNode.insertBefore(newNode, referenceNode.nextSibling);
}

//------------------------------------------------------------------------------
// vim: set ts=4 sw=4 tw=0 et :
