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

  getPercb(): number;
  setPercb(value: number): void;

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
    percb: number,
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

  clearBlotchidsList(): void;
  getBlotchidsList(): Array<number>;
  setBlotchidsList(value: Array<number>): void;
  addBlotchids(value: number, index?: number): number;

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
    blotchidsList: Array<number>,
  }
}

export class PickedCircle extends jspb.Message {
  getCenterrow(): number;
  setCenterrow(value: number): void;

  getCentercol(): number;
  setCentercol(value: number): void;

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
    centerrow: number,
    centercol: number,
    radius: number,
    imgfilename: string,
  }
}

export class FolderImage extends jspb.Message {
  getFilename(): string;
  setFilename(value: string): void;

  getThumbnailimgvfn(): string;
  setThumbnailimgvfn(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): FolderImage.AsObject;
  static toObject(includeInstance: boolean, msg: FolderImage): FolderImage.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: FolderImage, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): FolderImage;
  static deserializeBinaryFromReader(message: FolderImage, reader: jspb.BinaryReader): FolderImage;
}

export namespace FolderImage {
  export type AsObject = {
    filename: string,
    thumbnailimgvfn: string,
  }
}

export class ScanFolder extends jspb.Message {
  clearFolderimagesList(): void;
  getFolderimagesList(): Array<FolderImage>;
  setFolderimagesList(value: Array<FolderImage>): void;
  addFolderimages(value?: FolderImage, index?: number): FolderImage;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ScanFolder.AsObject;
  static toObject(includeInstance: boolean, msg: ScanFolder): ScanFolder.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ScanFolder, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ScanFolder;
  static deserializeBinaryFromReader(message: ScanFolder, reader: jspb.BinaryReader): ScanFolder;
}

export namespace ScanFolder {
  export type AsObject = {
    folderimagesList: Array<FolderImage.AsObject>,
  }
}

export class ReadBlotch extends jspb.Message {
  hasCircle(): boolean;
  clearCircle(): void;
  getCircle(): PickedCircle | undefined;
  setCircle(value?: PickedCircle): void;

  hasStats(): boolean;
  clearStats(): void;
  getStats(): PickStats | undefined;
  setStats(value?: PickStats): void;

  getContextvfn(): string;
  setContextvfn(value: string): void;

  getComparevfn(): string;
  setComparevfn(value: string): void;

  getBlotchid(): number;
  setBlotchid(value: number): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ReadBlotch.AsObject;
  static toObject(includeInstance: boolean, msg: ReadBlotch): ReadBlotch.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ReadBlotch, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ReadBlotch;
  static deserializeBinaryFromReader(message: ReadBlotch, reader: jspb.BinaryReader): ReadBlotch;
}

export namespace ReadBlotch {
  export type AsObject = {
    circle?: PickedCircle.AsObject,
    stats?: PickStats.AsObject,
    contextvfn: string,
    comparevfn: string,
    blotchid: number,
  }
}

export class ActiveImage extends jspb.Message {
  getFilename(): string;
  setFilename(value: string): void;

  getImgdatavfn(): string;
  setImgdatavfn(value: string): void;

  clearReadblotchesList(): void;
  getReadblotchesList(): Array<ReadBlotch>;
  setReadblotchesList(value: Array<ReadBlotch>): void;
  addReadblotches(value?: ReadBlotch, index?: number): ReadBlotch;

  getDownsamplefactor(): number;
  setDownsamplefactor(value: number): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): ActiveImage.AsObject;
  static toObject(includeInstance: boolean, msg: ActiveImage): ActiveImage.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: ActiveImage, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): ActiveImage;
  static deserializeBinaryFromReader(message: ActiveImage, reader: jspb.BinaryReader): ActiveImage;
}

export namespace ActiveImage {
  export type AsObject = {
    filename: string,
    imgdatavfn: string,
    readblotchesList: Array<ReadBlotch.AsObject>,
    downsamplefactor: number,
  }
}

export class UIState extends jspb.Message {
  hasOpenfolder(): boolean;
  clearOpenfolder(): void;
  getOpenfolder(): ScanFolder | undefined;
  setOpenfolder(value?: ScanFolder): void;

  getSelectedfolderimgidx(): number;
  setSelectedfolderimgidx(value: number): void;

  hasActiveimage(): boolean;
  clearActiveimage(): void;
  getActiveimage(): ActiveImage | undefined;
  setActiveimage(value?: ActiveImage): void;

  hasClipboardcontent(): boolean;
  clearClipboardcontent(): void;
  getClipboardcontent(): ClipboardContent | undefined;
  setClipboardcontent(value?: ClipboardContent): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): UIState.AsObject;
  static toObject(includeInstance: boolean, msg: UIState): UIState.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: UIState, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): UIState;
  static deserializeBinaryFromReader(message: UIState, reader: jspb.BinaryReader): UIState;
}

export namespace UIState {
  export type AsObject = {
    openfolder?: ScanFolder.AsObject,
    selectedfolderimgidx: number,
    activeimage?: ActiveImage.AsObject,
    clipboardcontent?: ClipboardContent.AsObject,
  }
}

