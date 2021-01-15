// package: 
// file: types.proto

import * as jspb from "google-protobuf";

export class PickStats extends jspb.Message {
  getMur(): number;
  setMur(value: number): void;

  getMug(): number;
  setMug(value: number): void;

  getMub(): number;
  setMub(value: number): void;

  getPercr(): number;
  setPercr(value: number): void;

  getPercg(): number;
  setPercg(value: number): void;

  getPrecb(): number;
  setPrecb(value: number): void;

  getSigmar(): number;
  setSigmar(value: number): void;

  getSigmag(): number;
  setSigmag(value: number): void;

  getSigmab(): number;
  setSigmab(value: number): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): PickStats.AsObject;
  static toObject(includeInstance: boolean, msg: PickStats): PickStats.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: PickStats, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): PickStats;
  static deserializeBinaryFromReader(message: PickStats, reader: jspb.BinaryReader): PickStats;
}

export namespace PickStats {
  export type AsObject = {
    mur: number,
    mug: number,
    mub: number,
    percr: number,
    percg: number,
    precb: number,
    sigmar: number,
    sigmag: number,
    sigmab: number,
  }
}

export class ClipboardContent extends jspb.Message {
  clearRowsList(): void;
  getRowsList(): Array<PickStats>;
  setRowsList(value: Array<PickStats>): void;
  addRows(value?: PickStats, index?: number): PickStats;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ClipboardContent.AsObject;
  static toObject(includeInstance: boolean, msg: ClipboardContent): ClipboardContent.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ClipboardContent, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ClipboardContent;
  static deserializeBinaryFromReader(message: ClipboardContent, reader: jspb.BinaryReader): ClipboardContent;
}

export namespace ClipboardContent {
  export type AsObject = {
    rowsList: Array<PickStats.AsObject>,
  }
}

export class PickedCircle extends jspb.Message {
  getCenterx(): number;
  setCenterx(value: number): void;

  getCentery(): number;
  setCentery(value: number): void;

  getRadius(): number;
  setRadius(value: number): void;

  getImgfilename(): string;
  setImgfilename(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): PickedCircle.AsObject;
  static toObject(includeInstance: boolean, msg: PickedCircle): PickedCircle.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: PickedCircle, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): PickedCircle;
  static deserializeBinaryFromReader(message: PickedCircle, reader: jspb.BinaryReader): PickedCircle;
}

export namespace PickedCircle {
  export type AsObject = {
    centerx: number,
    centery: number,
    radius: number,
    imgfilename: string,
  }
}

