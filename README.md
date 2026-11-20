


Reasonably we could do this without PassioGO.

Maybe we could do this without any external API at all...

The only information I use from them is the live bus location, and that can be done with an esp32 GPS

This would also be a good reason to get involved with meshNYC




THE GOAL:
    #a screen that displays when the bus gets to a stop 


    The ideal program would use allow the user to register STOP LOCATIONS

    from there, the STOP LOCATIONS reveal the ROUTES

    then we get all the BUS LOCATIONS, and filter for only busses on the ROUTES we want




    We then take those filtered BUS LOCATIONS and compare each to it's PLOTTED ROUTE

    we know each bus travels along it's PLOTTED ROUTE from it's current location to the STOP associated with the call being made

    each bus is now associated with the exact PLOTTED ROUTE it will be taking

    this data is then passed through an algorithm which converts domains over NYC to time estimates

    and this is all made accessible via an internal python server



    then a local website being played on the kiosk would ping the internal python server to get the data to display







NOTES:

    free tomtom works

    WGS 84 standard coords for compute



    osrm vs valhalla?




TO DO:

    achieve heaven

    formalize API json format


    MVP website



    config:
        AP  
        local website
        school wifi creds
        local AP pass
        stop
        tomtom api key



    account for:
        system alerts
        bus schedule spreadsheet


    auto download the map KMZs

    audo download the bus schedule spreadsheets

    depart from TOMTOM API
