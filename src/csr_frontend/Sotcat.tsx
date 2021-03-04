import { NONAME } from 'dns';
import React from 'react';
import { PickedCircle, ClipboardContent, PickStats, UIState, FolderImage, ActiveImage, ReadBlotch, ClipboardViewColumns } from './protobuf_js/types_pb'

let BOX_SHADOW_STR: string = "0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)";

type PlatformProps = {
  imagesInputButton: JSX.Element,
}

class SotcatContainer extends React.Component<{platformProps: PlatformProps}, {uiState: UIState}> {

  constructor(props: {platformProps: PlatformProps}) {
    super(props)
    this.state = {
      uiState: new UIState()
    }
  }

  render() {
    return (
      <div style = {{
        backgroundColor: "dimgray",
        fontFamily: "Noto Sans JP, sans-serif",
      }}>
        <Sotcat
          uiState = {this.state.uiState}
          request = {this.do_request.bind(this)}
          baseURL = {'http://localhost:8000'}
          platformProps = {this.props.platformProps}
        />
      </div>
    )
  }

  do_request(url: string, body: any = undefined) {

    let fetchProm;

    if (body) {
      fetchProm = fetch(url, {
        method: 'POST',
        body: body
      });
    } else {
      fetchProm = fetch(url);
    }
    fetchProm.then((res: Response) => {
      console.log(res);
      return res.arrayBuffer()
    }).then((buff: ArrayBuffer) => {
      let uiState = UIState.deserializeBinary(buff as Uint8Array);
      console.log(uiState.toObject());
      this.setState({
        uiState: uiState
      });
    })
  }
}

type SotcatProps = {
  uiState: UIState,
  request: (url: string, body?: any) => void,
  baseURL: string,
  platformProps: PlatformProps,
}

type SotcatState = {
  clipboardContent: ClipboardContent,
  selectedScanFname: string,
}

type Point = {
  x: number,
  y: number,
}


class Sotcat extends React.Component<SotcatProps, SotcatState> {

  amDrawingCircle: boolean;
  circleCenter?: Point;
  canvasRef: React.RefObject<HTMLCanvasElement>;
  imgElement: HTMLImageElement;

  constructor(props: SotcatProps) {
    super(props);
    this.state = {
      clipboardContent: new ClipboardContent(),
      selectedScanFname: "",
    }
    this.amDrawingCircle = false;
    this.circleCenter = undefined;
    this.canvasRef = React.createRef();
    this.imgElement = new Image();
    console.log('Socat.constructor()')

  }

  componentDidMount() {
    // fetch('http://localhost:8000/pic')
    //   .then(res => res.json())
    //   .then(
    //     (result) => {
    //       console.log(result);
    //       // this.setState({
    //       //   imgData: result.imgData
    //       // })
    //       // let img = <img
    //       //   src={`data:image/png;base64,${imgData}`}
    //       //   width="800"
    //       // />;
    //       let img = new Image();
    //       // window.globals = {};
    //       // window.globals.img = img;
    //       // window.globals.ctx = this.ctx;
    //       img.src = `data:image/png;base64,${result.imgData}`;
    //       img.onload = () => {
    //         console.log("img.onload");

    //         this.setState({
    //           img: img,
    //         }, () => {
    //           this.canvasRef.current!.getContext("2d")!.drawImage(img, 0, 0, img.width * this.imgScale, img.height * this.imgScale);
    //         })

    //       }
    //     }
    //   )
  }

  render() {
    console.log("Sotcat.render()");
    return (
      <div style={{
        // border: "1px solid black",
        boxShadow: BOX_SHADOW_STR,
        // backgroundColor: "rgba(252, 210, 207, 0.8)"
        backgroundColor: "dimgray",
        borderRadius: 5,
      }}>
        <ScanViewer
          uiState = {this.props.uiState}
          request = {this.props.request}
          baseURL = {this.props.baseURL}
          imagesInputButton = {this.props.platformProps.imagesInputButton}
        />
        <div style = {{
          boxShadow: BOX_SHADOW_STR,
          borderRadius: 5,
          minHeight: 30,
          display: "flex",
          margin: 3,
          marginTop: 5,
          marginBottom: 5,
        }}>
          <CSRMenu
            acImg = {this.props.uiState.getActiveimage()!}
            cbCols = {this.props.uiState.getClipboardviewcolumns()!}
            request = {this.props.request}
            baseURL = {this.props.baseURL}
          />
        </div>
        <div
          style={{
            display: "flex",
            flexDirection: "row",
            marginTop: 5,
            boxShadow: BOX_SHADOW_STR,
            borderRadius: 5,
            margin: 3,
          }}
        >

          <div style={{
            display: "inline-block",
          }}>
          <canvas
              id="canvas"
              // width={(this.state.img && this.state.img!.width * this.imgScale) || "1600"}
              // height={(this.state.img && this.state.img!.height * this.imgScale) || "1000"}
              // width = "1600"
              // height = "1000"
              ref={this.canvasRef}
              onMouseDown={(event: React.MouseEvent<HTMLCanvasElement, MouseEvent>) => {
                let canvas: HTMLCanvasElement = event.target as HTMLCanvasElement;

                if (this.amDrawingCircle) {
                  this.amDrawingCircle = false;
                  // return;

                  let imgScale = this.props.uiState.getActiveimage()?.getZoomratiosrcimg()! / this.props.uiState.getActiveimage()?.getZoomratioviewimg()!;

                  // let imgScale = this.props.uiState.getActiveimage()?.getDownsamplefactor()!

                  this.postCircle(
                    {
                      x: this.circleCenter!.x * imgScale,
                      y: this.circleCenter!.y * imgScale,
                    },
                    this.getRadius(this.circleCenter!, this.getMousePosOnCanvas(canvas, event)) * imgScale
                  );
                  return;
                }
                this.amDrawingCircle = true;
                let pointer = this.getMousePosOnCanvas(canvas, event);
                this.circleCenter = pointer;

                let ctx = canvas.getContext("2d")!;


                this.drawCircle(ctx, pointer, 4, 'black');
                this.drawCircle(ctx, pointer, 6, 'black');
                this.drawCircle(ctx, pointer, 5, 'white');
              }}
              onMouseMove={(event) => {
                let canvas: HTMLCanvasElement = event.target as HTMLCanvasElement;

                if (!this.amDrawingCircle) {
                  return;
                }

                let pointer = this.getMousePosOnCanvas(canvas, event);

                let radius = this.getRadius(this.circleCenter!, pointer);

                if (radius > 2) {
                  let ctx = canvas.getContext("2d")!;

                  ctx.clearRect(0, 0, canvas.width, canvas.height);
                  // ctx.drawImage(this.state.img!, 0, 0, this.state.img!.width * this.imgScale, this.state.img!.height * this.imgScale);
                  ctx.drawImage(this.imgElement, 0, 0);
                  this.drawSelection(ctx, this.circleCenter!, radius);
                }
              }
            }
            style = {{
              backgroundImage: this.props.baseURL + '/image_bytes/' + this.props.uiState.getActiveimage()?.getImgdatavfn(),
              // border: "1px solid red"
              boxShadow: BOX_SHADOW_STR,
              margin: 3,
              borderRadius: 5,
              border: "1px solid rgba(0, 0, 0, 0.2)",
            }}
            >
              {/* <img src = {this.props.baseURL + '/image_bytes/' + this.props.uiState.getActiveimage()?.getImgdatavfn()}/> */}
            </canvas>
          </div>
        <div style={{
          display: "flex",
        }}>
          <ClipboardView
            content={this.props.uiState.getClipboardcontent() || new ClipboardContent()}
            cbCols={this.props.uiState.getClipboardviewcolumns() || new ClipboardViewColumns()}
            baseURL = {this.props.baseURL}
            request = {this.props.request}
          />
        </div>
        </div>
        <div style={{
          display: "flex",
          // flexDirection: "row",
          // overflow: "scroll",
        }}>
          {/* {this.state.drops} */}
          <BlotchCircleDisp
            blotches = {this.props.uiState.getActiveimage()?.getReadblotchesList() || []}
            baseURL = {this.props.baseURL}
          />
        </div>
      </div>
    )
  }

  componentDidUpdate() {
    this.imgElement = new Image();
    this.imgElement.src = this.props.baseURL + '/image_bytes/' + this.props.uiState.getActiveimage()?.getImgdatavfn();
    this.imgElement.onload = () => {
      this.canvasRef.current!.width = this.imgElement.width;
      this.canvasRef.current!.height = this.imgElement.height;
      this.canvasRef.current!.getContext('2d')!.drawImage(this.imgElement, 0, 0);
    }
  }

  drawSelection(ctx: CanvasRenderingContext2D, centerXY: Point, radius: number) {
    this.drawCircle(ctx, centerXY, radius - 1, 'black');
    this.drawCircle(ctx, centerXY, radius + 1, 'black');
    this.drawCircle(ctx, centerXY, radius, 'white');
  }

  postCircle(center: { x: number, y: number }, radius: number) {

    let pc = new PickedCircle();
    pc.setCentercol(center.x);
    pc.setCenterrow(center.y);
    pc.setRadius(radius);
    pc.setImgfilename(this.props.uiState.getActiveimage()?.getFilename()!);

    let msg = pc.serializeBinary();

    this.props.request(this.props.baseURL + '/new_circle', msg);

    // fetch('http://localhost:8000/new_circle', {
    //   method: 'POST',
    //   // body: JSON.stringify({
    //   //   center: center,
    //   //   radius: radius,
    //   //   fname: this.state.selectedScanFname,
    //   // })
    //   body: msg,
    // }).then(res => res.json())
    //   .then((result) => {
    //     console.log(result);
    //     this.setState(prevState => ({
    //       drops: [...prevState.drops, <Drop
    //         contextPicB64={result.circContext}
    //         colourComparePicB64={result.colourCompare}
    //         key={this.state.drops.length}
    //       />],
    //       clipboardContent: ClipboardContent.deserializeBinary(result.clipboardContent),
    //     }))
    //   })
  }

  drawCircle(ctx: CanvasRenderingContext2D, locXY: Point, radius: number, colour: string) {
    ctx.beginPath();
    ctx.strokeStyle = colour;
    ctx.arc(locXY.x, locXY.y, radius, 0, 2 * Math.PI);
    ctx.closePath();
    ctx.stroke();
  }

  getMousePosOnCanvas(canvas: HTMLCanvasElement, event: React.MouseEvent<HTMLCanvasElement, MouseEvent>) {
    let rect = canvas.getBoundingClientRect();
    return {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
    }
  }

  getRadius(center: Point, pointer: Point) {
    return Math.sqrt(
      (pointer.x - center.x) ** 2 + (pointer.y - center.y) ** 2
    ) / 5;
  }
}

// ReactDOM.render(
//   <Socat />,
//   document.getElementById('root')
// );

type DropProps = {
  contextVFN: string,
  compareVFN: string,
  baseURL: string,
};

type DropState = {

};

class Drop extends React.Component<DropProps, DropState> {

  constructor(props: DropProps) {
    super(props)
  }

  render() {
    return (
      <div style={{
        // border: "1px solid blue",
        // marginLeft: 3,
        // marginRight:
        // borderRadius: 3,
        marginLeft: 3,
        marginRight: 3,
        display: "flex",
        flexDirection: "column",
        border: "1px solid rgba(0, 0, 0, 0.2)",
      }}>
          <img
            // src={`data:image/png;base64,${this.props.contextPicB64}`}
            src = {this.props.baseURL + '/image_bytes/' + this.props.contextVFN}
            width="150"
            style = {{
              // borderRadius: 3,
              // border: "1px solid rgba(0, 0, 0, 0.2)",
            }}
          />
          <img
            // src={`data:image/png;base64,${this.props.colourComparePicB64}`}
            src = {this.props.baseURL + '/image_bytes/' + this.props.compareVFN}
            width="150"
            style = {{
              // borderRadius: 3,
              // border: "1px solid rgba(0, 0, 0, 0.2)",
            }}
          />
      </div>
    )
  }
}

type ClipboardViewProps = {
  content: ClipboardContent;
  cbCols: ClipboardViewColumns;
  baseURL: string;
  request: (url: string) => void;
}

class ClipboardView extends React.Component<ClipboardViewProps, {}> {

  thStyle = {textAlign: "center",  width: 40,};
  trStyle = {
    borderBottom: "1px solid rgba(0, 0, 0, 0.2)",
  };

  render() {
    return (
      <table style = {{
        boxShadow: "0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)",
        border: "1px solid rgba(0, 0, 0, 0.2)",
        borderRadius: 5,
        margin: 3,
        borderCollapse: "collapse",
      }}>
        <thead style = {{
          borderBottom: "1px solid gray",
          borderRadius: 5,
        }}>
          <tr style = {this.trStyle}>
            {/* {["🎨", "μR", "μG", "μB","%R", "%G", "%B", "σR", "σG", "σB", "px", "➖"].map((header, idx) => {
              console.log(idx, idx % 3 == 1);
              return (
              <th style = {{
                textAlign: "center",
                width: 40,
                borderRight: idx % 3 == 0 ? "1px solid rgba(0, 0, 0, 0.2)" : undefined
              }}>{header}</th>
              );
            })} */}
            {[
              this._render_th("🎨", true)
            ].concat(this.props.cbCols.getName() ? [
              this._render_th("ID", true)
            ] : []).concat(this.props.cbCols.getMurgb() ? [
              this._render_th("μR", false),
              this._render_th("μG", false),
              this._render_th("μB", true),
            ] : []).concat(this.props.cbCols.getPercrgb() ? [
              this._render_th("%R", false),
              this._render_th("%G", false),
              this._render_th("%B", true),
            ] : []).concat(this.props.cbCols.getSigmargb() ? [
              this._render_th("σR", false),
              this._render_th("σG", false),
              this._render_th("σB", true),
            ] : []).concat(this.props.cbCols.getNumpixels() ? [
              this._render_th("px", true),
            ] : []).concat([
              this._render_th("➖", false)
            ])}
          </tr>
        </thead>
        <tbody>
          {this.props.content.getRowsList().map((row: PickStats, idx: number) =>
            <tr style = {this.trStyle}>
              {[
                <td style = {{
                  borderRight: "1px solid rgba(0, 0, 0, 0.2)",
                }}>
                  <div style = {{
                    backgroundColor: `rgb(${[row.getMur(), row.getMug(), row.getMub()].join(",")})`,
                    width: 20,
                    marginLeft: 10,
                    height: "100%",
                    borderRadius: 2,
                  }}/>
                </td>
              ].concat(this.props.cbCols.getName() ? [
                this._render_td("", true)
              ] : []).concat(this.props.cbCols.getMurgb() ? [
                this._render_td(row.getMur().toFixed(2), false),
                this._render_td(row.getMug().toFixed(2), false),
                this._render_td(row.getMub().toFixed(2), true),
              ] : []).concat(this.props.cbCols.getPercrgb() ? [
                this._render_td(row.getPercr().toFixed(2), false),
                this._render_td(row.getPercg().toFixed(2), false),
                this._render_td(row.getPercb().toFixed(2), true),
              ] : []).concat(this.props.cbCols.getSigmargb() ? [
                this._render_td(row.getSigmar().toFixed(2), false),
                this._render_td(row.getSigmag().toFixed(2), false),
                this._render_td(row.getSigmab().toFixed(2), true),
              ] : []).concat(this.props.cbCols.getNumpixels() ? [
                this._render_td(row.getNumpixels().toString(), true),
              ] : [])
              // .concat([row.getMur(), row.getMug(), row.getMub(), row.getPercr(), row.getPercg(), row.getPercb(), row.getSigmar(), row.getSigmag(), row.getSigmab(), row.getNumpixels()].map((elt, idx) =>
              //   <td style={{
              //     textAlign: "center",
              //     borderRight: idx % 3 == 2 ? "1px solid rgba(0, 0, 0, 0.2)" : undefined,
              //     fontSize: "8pt",
              //   }}>
              //     {elt.toFixed(2)}
              //   </td>
              .concat([
                <td style = {{
                  // overflow: 'hidden',
                  justifyContent: "center",
                  alignItems: "center",
                  display: "flex",
                }}>
                  {/* <div style = {{
                    width: 20,
                    height: "100%",
                    // justifyContent: "center",
                    // alignItems: "center",
                    marginLeft: 9,
                    borderRadius: 3,
                    backgroundColor: "rgba(255, 255, 255, 0.3)"
                  }}
                    onClick
                  >
                    ➖
                  </div> */}
                  <button
                    style = {{
                      marginLeft: 2,
                      marginRight: 2,
                      backgroundColor: "rgba(255, 255, 255, 0.4)",
                      border:"1px solid rgba(0, 0, 0, 0.5)",
                      height: "100%",
                      fontSize: "8pt",
                      display: "flex",
                    }}
                    onClick = {() => {
                      console.log("Remove blotch request for ", this.props.content.getBlotchidsList()[idx]);
                      this.props.request(this.props.baseURL + "/remove_blotch/" + this.props.content.getBlotchidsList()[idx]);
                    }}
                  >
                    ➖
                  </button>
                </td>
              ])}
            </tr>
          )}
        </tbody>
      </table>
    )
  }

  _render_th(name: string, border: boolean) {
    return (
      <th
        style = {{
          textAlign: "center",
          width: 40,
          borderRight: border ? "1px solid rgba(0, 0, 0, 0.2)" : undefined,
        }}
      >{name}</th>
    )
  }

  _render_td(text: string, border: boolean) {
    return (
      <td style={{
        textAlign: "center",
        borderRight: border ? "1px solid rgba(0, 0, 0, 0.2)" : undefined,
        fontSize: "8pt",
      }}>
        {text}
      </td>
    )
  }

  _render_mu() {

  }

}

type ScanViewerProps = {
  uiState: UIState;
  request: (url: string) => void;
  baseURL: string;
  imagesInputButton: JSX.Element;
}

class ScanViewer extends React.Component<ScanViewerProps, {}> {

  selectedTNRef: React.RefObject<HTMLImageElement>;
  scansDivRef: React.RefObject<HTMLDivElement>;

  BUTTON_STYLE = {
    backgroundColor: "whitesmoke",
    borderRadius: "10px",
    border: "none",
    fontSize: "1.3rem",
    boxShadow: "0px 8px 28px -6px rgba(24, 39, 75, 0.12), 0px 18px 88px -4px rgba(24, 39, 75, 0.14)",
    transition: "transform ease-in 0.1s",
  }

  constructor(props: ScanViewerProps) {
    super(props)

    this.selectedTNRef = React.createRef();
    this.scansDivRef = React.createRef();
  }

  render() {
    return (
      <div style={{
        // border: "1px solid black",
        boxShadow: "0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)",
        display: "flex",
        flexDirection: "row",
        width: "100%",
        minHeight: 100,
        borderRadius: 5,
      }}>
        <div>
          {/* <button
            style={Object.assign(this.BUTTON_STYLE, {
              height: "90%",
              width: 70,
              fontSize: 12,
              margin: 3,
            })}
            onClick={() => {
              this.props.request(this.props.baseURL + '/open_folder');
            }}
          >Open Folder</button> */}
          {this.props.imagesInputButton}
        </div>
        <div>
          <button
            style={Object.assign(this.BUTTON_STYLE, {
              height: "90%",
              width: 50,
              margin: 3,
            })}
            onClick={() => {
              this._on_selection(this.props.uiState.getSelectedfolderimgidx() - 1);
            }}
          >◀</button>
        </div>
        <div>
          <button
            style={Object.assign(this.BUTTON_STYLE, {
              width: 50,
              height: "90%",
              margin: 3,
            })}
            onClick={() => {
              this._on_selection(this.props.uiState.getSelectedfolderimgidx() + 1);
            }}
          >▶</button>
        </div>
        <div
          style={{
            overflowX: "auto",
            whiteSpace: "nowrap",
          }}
          ref={this.scansDivRef}
        >
          <div style = {{
            // overflowX: "scroll",
          }}>
            {this.props.uiState.getOpenfolder()?.getFolderimagesList().map((fi: FolderImage, idx) => (
              <img
                key={idx}
                src={this.props.baseURL + "/image_bytes/" + fi.getThumbnailimgvfn()}
                width="150"
                style={idx == this.props.uiState.getSelectedfolderimgidx() ? {
                  border: "3px solid rgb(112, 167, 255)",
                  borderRadius: 5,
                  boxShadow: "0 4px 8px 0 rgba(0, 0, 50, 0.4), 0 6px 20px 0 rgba(0, 0, 50, 0.4)",
                  marginRight: 3,
                } : {
                  marginRight: 3,
                  borderRadius: 3,
                }}
                ref={idx == this.props.uiState.getSelectedfolderimgidx() ? this.selectedTNRef : undefined}
                onClick={() => {
                  this._on_selection(idx);
              }}
              />
            ))}
          </div>
        </div>
      </div>
    )
  }

  componentDidUpdate() {
    let selectedPos = this.selectedTNRef.current!.offsetLeft;
    this.scansDivRef.current!.scrollLeft = selectedPos - 400;
  }

  _on_selection(selectedIdx: number) {
    if (selectedIdx == this.props.uiState.getSelectedfolderimgidx() || selectedIdx < 0 || selectedIdx >= this.props.uiState.getOpenfolder()!.getFolderimagesList()!.length) {
      return;
    }
    let url = new URL('http://localhost:8000/select_scan')
    url.search = new URLSearchParams({
      fname: this.props.uiState.getOpenfolder()?.getFolderimagesList()[selectedIdx].getFilename()!,
      selectedIdx: selectedIdx.toString(),
    }).toString();
    this.props.request(url.toString());

    // this.props.onScanSelected(this.state.thumbnails[selectedIdx].fileName);
    // this.setState({
    //   selectedIdx: selectedIdx
    // }, () => {
    //   let selectedPos = this.selectedTNRef.current!.offsetLeft;
    //   console.log(selectedPos);
    //   this.scansDivRef.current!.scrollLeft = selectedPos - 400;
    // })
  }
}

type BlotchCircleDispProps = {
  blotches: Array<ReadBlotch>,
  baseURL: string,
}

class BlotchCircleDisp extends React.Component<BlotchCircleDispProps, {}> {

  render() {
    return (
      <div style = {{
        display: "flex",
        flexDirection: "row",
        // overflowX: "scroll",
        overflowX: "auto",
        width: "100%",
        margin: 3,
        borderRadius: 5,
        boxShadow: BOX_SHADOW_STR,
        border: "1px solid rgba(0, 0, 0, 0.2)",
        minHeight: 100,
      }}>
        {this.props.blotches.map((rb: ReadBlotch) => {
          return (<Drop
            baseURL = {this.props.baseURL}
            contextVFN = {rb.getContextvfn()}
            compareVFN = {rb.getComparevfn()}
          />)
        })}
      </div>
    )
  }
}

type CSRMenuProps = {
  acImg: ActiveImage,
  cbCols: ClipboardViewColumns,
  request: (url: string, body?: any) => void,
  baseURL: string,
};

class CSRMenu extends React.Component<CSRMenuProps, {}> {

  // SCALE_MARKS: Array<number> = [1/8, 1/4, 1/2, 1, 2, 4, 8];
  // marks: Array<any>;

  ZOOM_RATIO_VIEW_TO_SRC: Array<Array<number>> = [[1, 16], [1, 8], [1, 4], [1, 2], [1, 1], [2, 1], [4, 1], [8, 1]]

  constructor(props: CSRMenuProps) {
    super(props);

    // this.marks = this.SCALE_MARKS.map(elt => {
    //   return {
    //     value: elt,
    //     label: elt.toString(),
    //   }
    // })
  }

  _get_idx_of_ratio(viewRatio: number, srcRatio: number) {
    let idx = -1;
    this.ZOOM_RATIO_VIEW_TO_SRC.forEach(
      (elt, i) => {
        if (elt[0] == viewRatio && elt[1] == srcRatio) {
          idx = i;
        }
      }
    );
    return idx;
  }

  render() {
    if (this.props.acImg == undefined) {
      return (<div></div>)
    }
    return (
      <div style = {{
        display: "flex",
        flexDirection: "row",
      }}>
        <div style = {{
          height: "100%",
          display: "flex",
          flexDirection: "row",
          alignItems: "center",
        }}>
          <label
              htmlFor ="zoom"
              style = {{
                marginLeft: 5,
                marginRight: 3,
              }}
            >Zoom: </label>
            <input
              type="range" id="zoom" name="zoom"
              min="0" max = {this.ZOOM_RATIO_VIEW_TO_SRC.length-1}
              value = {
                this._get_idx_of_ratio(this.props.acImg.getZoomratioviewimg(), this.props.acImg.getZoomratiosrcimg())
              }
              style = {{
                marginLeft: 5,
              }}
              width = {150}
              onChange = {(event: React.ChangeEvent<HTMLInputElement>) => {
                // console.log(event);
                console.log(event.target.value);

                let ratio = this.ZOOM_RATIO_VIEW_TO_SRC[event.target.value as unknown as number];

                let viewRatio = ratio[0];
                let srcRatio = ratio[1];
                this.props.request(this.props.baseURL + `/set_zoom/${viewRatio}/${srcRatio}`)
              }}
            ></input>
            <span style = {{
              marginLeft: 5,
            }}>
              {`${this.props.acImg.getZoomratioviewimg()!}:${this.props.acImg.getZoomratiosrcimg()}`}
            </span>
        </div>
        <div style = {{
          marginLeft: 20,
          borderLeft: "1px solid rgba(0, 0, 0, 0.2)",
          paddingLeft: 20,
        }}>
            <span style = {{
              marginRight: 10,
            }}>
              Columns:
            </span>
            {[
              this._render_column_toggle(
                'ID',  this._sel_cols().getName(),
                (cols: ClipboardViewColumns, val: boolean) => cols.setName(val)
              ),
              this._render_column_toggle(
                'μRGB',  this._sel_cols().getMurgb(),
                (cols: ClipboardViewColumns, val: boolean) => cols.setMurgb(val)
              ),
              this._render_column_toggle(
                '%RGB', this._sel_cols().getPercrgb(),
                (cols: ClipboardViewColumns, val: boolean) => cols.setPercrgb(val)
              ),
              this._render_column_toggle(
                'σRGB', this._sel_cols().getSigmargb(),
                (cols: ClipboardViewColumns, val: boolean) => cols.setSigmargb(val)
              ),
              this._render_column_toggle(
                '#PX', this._sel_cols().getNumpixels(),
                (cols: ClipboardViewColumns, val: boolean) => cols.setNumpixels(val)
              ),
            ]}
        </div>
      </div>
    )
  }

  _render_column_toggle(text: string, selected: boolean, colsModifyer: (cols: ClipboardViewColumns, val: boolean) => void) {
    return (
      <button style = {{
        backgroundColor: selected ? "rgba(255, 255, 255, 0.2)" : "rgba(255, 255, 255, 0.1)",
        fontSize: "1em",
        color: selected ? "white" : "rgb(200, 200, 200)",
        borderRadius: 3,
        height: "100%",
        fontWeight: "bold",
        border: selected ? "1px solid rgba(255, 255, 255, 0.3)" : "1px solid rgba(255, 255, 255, 0.2)",
        marginLeft: 2,
        marginRight: 2,
      }}
        onClick = {() => {
          this._toggle_column(colsModifyer, !selected);
        }}
      >
        {text}
      </button>
    )
  }

  _sel_cols(): ClipboardViewColumns {
    return this.props.cbCols;
  }

  _toggle_column(
    modifyer: (cols: ClipboardViewColumns, val: boolean) => void,
    val: boolean
  ) {

    let cvc: ClipboardViewColumns = ClipboardViewColumns.deserializeBinary(this.props.cbCols.serializeBinary());

    modifyer(cvc, val);

    this.props.request(this.props.baseURL + "/set_clipboard_cols", cvc.serializeBinary());
  }
}

export default SotcatContainer;
