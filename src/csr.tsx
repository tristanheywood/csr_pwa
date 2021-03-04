import React from 'react';
import SotcatContainer from './csr_frontend/Sotcat'

class ColorimetricSensorReader extends React.Component<{}, {}> {

    render() {
        return (
            <SotcatContainer
                platformProps = {{
                    imagesInputButton: <SelectImgsButton/>
                }}
            />
        )
    }
}

class SelectImgsButton extends React.Component<{}, {}> {

    render() {
        return (
            <div style = {{
                height: "100%",
            }}>
                <label htmlFor="images_upload_input"
                    style = {{
                        // height: 100,
                        paddingTop: 0,
                        paddingBottom: 50,
                        width: 70, 
                        fontSize: 12,
                        margin: 3,
                        backgroundColor: "whitesmoke",
                        whiteSpace: "pre-wrap"
                    }}
                >
                    {"Select\nImages"}
                </label>
                <input 
                    type = "file" 
                    id = "images_upload_input"
                    style = {{display: "none"}}
                    accept="image/png, images/jpeg"
                    multiple 
                    onChange = {(event) => {
                        console.log(event.target.files);
                    }}
                ></input>
            </div>
        )
    }
}

export default ColorimetricSensorReader;