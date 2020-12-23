import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'unknown-person-card',
  templateUrl: './unknown-person-card.component.html',
  styleUrls: ['./unknown-person-card.component.css']
})
export class UnknownPersonCardComponent implements OnInit {
  @Input() property : any

  constructor() { }

  ngOnInit() {
  }

}
